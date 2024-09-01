import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['check_in_date'] = pd.to_datetime(df['check_in_date'])
    df['check_out_date'] = pd.to_datetime(df['check_out_date'])
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    colors = {
        'background': '#F7F7F7',
        'text': '#333333',
        'primary': '#3498DB',
        'secondary': '#2ECC71',
        'accent': '#F39C12',
        'negative': '#E74C3C'
    }

    kpi_style = {
        'textAlign': 'center',
        'padding': '15px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
        'margin': '10px',
        'width': '220px',
        'height': '150px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between',
        'transition': 'all 0.3s ease'
    }

    room_type_options = [{'label': i, 'value': i} for i in df.room_type.unique()]

    filter_style = {
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'flex-end',
        'margin': '20px auto',
        'width': '90%',
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)'
    }

    app.layout = dbc.Container([
        html.Div([
            html.H1('Hotel Booking Dashboard', style={
                'textAlign': 'center',
                'color': colors['text'],
                'marginBottom': '30px',
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Room Type', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-room-type',
                        options=room_type_options,
                        value=df.room_type.unique().tolist(),
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['check_in_date'].min(),
                        end_date=df['check_out_date'].max(),
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0, 
                                style={'padding': '10px 20px', 'backgroundColor': colors['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'all 0.3s ease'})
                ])
            ], style=filter_style),
            
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='bookings-over-time')], width=6),
                dbc.Col([dcc.Graph(id='room-type-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='average-price-by-room')], width=6),
                dbc.Col([dcc.Graph(id='guest-composition')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px',
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('bookings-over-time', 'figure'),
         Output('room-type-distribution', 'figure'),
         Output('average-price-by-room', 'figure'),
         Output('guest-composition', 'figure'),
         Output('dropdown-room-type', 'value'),
         Output('date-picker-range', 'start_date'),
         Output('date-picker-range', 'end_date')],
        [Input('dropdown-room-type', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('reset-button', 'n_clicks')],
        [State('dropdown-room-type', 'options')]
    )
    def update_dashboard(room_types, start_date, end_date, reset_clicks, room_type_options):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if ctx.triggered_id == 'reset-button':
            room_types = [option['value'] for option in room_type_options]
            start_date = df['check_in_date'].min()
            end_date = df['check_out_date'].max()
        
        dff = df[df.room_type.isin(room_types) & 
                 (df.check_in_date >= start_date) & 
                 (df.check_out_date <= end_date)]
        
        total_bookings = len(dff)
        total_revenue = dff['total_price'].sum()
        average_price = dff['total_price'].mean()
        occupancy_rate = len(dff) / (len(df) * (end_date - start_date).days) * 100
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.check_in_date >= past_start_date) & 
                      (df.check_out_date <= past_end_date)]
        
        past_total_bookings = len(past_dff)
        past_total_revenue = past_dff['total_price'].sum()
        past_average_price = past_dff['total_price'].mean()
        past_occupancy_rate = len(past_dff) / (len(df) * (past_end_date - past_start_date).days) * 100
        
        def create_kpi_card(title, current_value, previous_value, format_str='{:,.0f}'):
            change = current_value - previous_value
            change_percentage = (change / previous_value) * 100 if previous_value != 0 else 0
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400', 'height': '20px'}),
                html.Div([
                    html.Span(format_str.format(current_value), style={'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['primary']}),
                ], style={'height': '30px'}),
                html.Div([
                    html.Span(f'Previous: {format_str.format(previous_value)}', style={'fontSize': '14px', 'color': colors['text']}),
                ], style={'height': '20px'}),
                html.Div([
                    html.Div([
                        html.Span(f'{"▲" if change > 0 else "▼"}', 
                                style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '16px', 'marginRight': '5px'}),
                        html.Span(f'{abs(change):.1f} ({abs(change_percentage):.1f}%)', 
                                style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '14px'})
                    ], style={'display': 'inline-block'})
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '20px'})
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Bookings', total_bookings, past_total_bookings),
            create_kpi_card('Total Revenue', total_revenue, past_total_revenue, '${:,.0f}'),
            create_kpi_card('Average Price', average_price, past_average_price, '${:,.2f}'),
            create_kpi_card('Occupancy Rate', occupancy_rate, past_occupancy_rate, '{:.1f}%')
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'stretch', 'flexWrap': 'wrap'})
        
        def update_chart_layout(fig):
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
                font_color=colors['text'],
                title_font_size=20,
                title_font_color=colors['primary'],
                legend_title_font_color=colors['primary'],
                legend_title_font_size=14,
                legend_font_size=12,
                clickmode='event+select',
                hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Rockwell"
            )
            )
            fig.update_xaxes(showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            return fig
        
        bookings_over_time = px.line(dff.groupby('check_in_date')['booking_id'].count().reset_index(), 
                          x='check_in_date', y='booking_id', 
                          title="Daily Bookings Over Time",
                          labels={'check_in_date': 'Date', 'booking_id': 'Number of Bookings'})
        bookings_over_time.update_traces(mode='lines+markers', hovertemplate='Date: %{x}<br>Bookings: %{y}')
        bookings_over_time = update_chart_layout(bookings_over_time)
        
        room_type_distribution = px.pie(dff, names='room_type', values='booking_id', title="Room Type Distribution",
                                   color_discrete_sequence=px.colors.qualitative.Set3)
        room_type_distribution = update_chart_layout(room_type_distribution)
        
        average_price_by_room = px.bar(dff.groupby('room_type')['total_price'].mean().reset_index(), 
                                       x='room_type', y='total_price', title="Average Price by Room Type",
                                       color_discrete_sequence=[colors['primary']], 
                                       labels={'room_type': 'Room Type', 'total_price': 'Average Price'})
        average_price_by_room = update_chart_layout(average_price_by_room)
        
        guest_composition = px.bar(dff, x='room_type', y=['num_adults', 'num_children'], 
                                   title="Guest Composition by Room Type",
                                   labels={'value': 'Number of Guests', 'variable': 'Guest Type'},
                                   barmode='stack')
        guest_composition = update_chart_layout(guest_composition)
        
        return kpi_indicators, bookings_over_time, room_type_distribution, average_price_by_room, guest_composition, room_types, start_date, end_date

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()