import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['meter_reading_date'] = pd.to_datetime(df['meter_reading_date'])
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
        'padding': '20px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
        'margin': '10px',
        'width': '200px',
        'transition': 'all 0.3s ease'
    }

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
            html.H1('Energy Usage Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Energy Provider', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-provider',
                        options=[{'label': i, 'value': i} for i in df.energy_provider.unique()],
                        value=df.energy_provider.unique().tolist(),
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['meter_reading_date'].min(),
                        end_date=df['meter_reading_date'].max(),
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
                dbc.Col([dcc.Graph(id='energy-usage-trend')], width=6),
                dbc.Col([dcc.Graph(id='energy-cost-trend')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='building-type-usage')], width=6),
                dbc.Col([dcc.Graph(id='energy-source-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('energy-usage-trend', 'figure'),
         Output('energy-cost-trend', 'figure'),
         Output('building-type-usage', 'figure'),
         Output('energy-source-distribution', 'figure')],
        [Input('dropdown-provider', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('energy-usage-trend', 'clickData'),
         Input('energy-cost-trend', 'clickData'),
         Input('building-type-usage', 'clickData'),
         Input('energy-source-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(providers, start_date, end_date, usage_click, cost_click, building_click, source_click, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df[df.energy_provider.isin(providers) & 
                 (df.meter_reading_date >= start_date) & 
                 (df.meter_reading_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.energy_provider.isin(providers) & 
                         (df.meter_reading_date >= start_date) & 
                         (df.meter_reading_date <= end_date)]
            elif input_id == 'energy-usage-trend' and usage_click:
                date = pd.to_datetime(usage_click['points'][0]['x'])
                dff = dff[dff['meter_reading_date'] == date]
            elif input_id == 'energy-cost-trend' and cost_click:
                date = pd.to_datetime(cost_click['points'][0]['x'])
                dff = dff[dff['meter_reading_date'] == date]
            elif input_id == 'building-type-usage' and building_click:
                building_type = building_click['points'][0]['x']
                dff = dff[dff['building_type'] == building_type]
            elif input_id == 'energy-source-distribution' and source_click:
                energy_source = source_click['points'][0]['label']
                dff = dff[dff['energy_source'] == energy_source]

        total_usage = dff['energy_usage_kwh'].sum()
        total_cost = dff['energy_cost_usd'].sum()
        avg_consumption = dff['energy_consumption_per_capita'].mean()
        avg_rating = dff['energy_rating'].mean()
        
        past_start_date = start_date - timedelta(days=30)
        past_end_date = end_date - timedelta(days=30)
        past_dff = df[df.energy_provider.isin(providers) & 
                      (df.meter_reading_date >= past_start_date) & 
                      (df.meter_reading_date <= past_end_date)]
        
        past_total_usage = past_dff['energy_usage_kwh'].sum()
        past_total_cost = past_dff['energy_cost_usd'].sum()
        past_avg_consumption = past_dff['energy_consumption_per_capita'].mean()
        past_avg_rating = past_dff['energy_rating'].mean()
        
        usage_change = total_usage - past_total_usage
        cost_change = total_cost - past_total_cost
        consumption_change = avg_consumption - past_avg_consumption
        rating_change = avg_rating - past_avg_rating
        
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.0f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Energy Usage (kWh)', total_usage, usage_change),
            create_kpi_card('Total Energy Cost (USD)', total_cost, cost_change),
            create_kpi_card('Avg Consumption per Capita', avg_consumption, consumption_change),
            create_kpi_card('Avg Energy Rating', avg_rating, rating_change)
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
        
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
                clickmode='event+select'
            )
            fig.update_xaxes(showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            return fig
        
        energy_usage_trend = px.line(dff, x='meter_reading_date', y='energy_usage_kwh', title="Energy Usage Trend",
                                     color_discrete_sequence=[colors['primary']], labels={'meter_reading_date': 'Date', 'energy_usage_kwh': 'Energy Usage (kWh)'})
        energy_usage_trend = update_chart_layout(energy_usage_trend)
        
        energy_cost_trend = px.line(dff, x='meter_reading_date', y='energy_cost_usd', title="Energy Cost Trend",
                                    color_discrete_sequence=[colors['primary']], labels={'meter_reading_date': 'Date', 'energy_cost_usd': 'Energy Cost (USD)'})
        energy_cost_trend = update_chart_layout(energy_cost_trend)
        
        building_type_usage = px.bar(dff.groupby('building_type')['energy_usage_kwh'].mean().reset_index(), 
                                     x='building_type', y='energy_usage_kwh', title="Average Energy Usage by Building Type",
                                     color_discrete_sequence=[colors['primary']], labels={'building_type': 'Building Type', 'energy_usage_kwh': 'Avg Energy Usage (kWh)'})
        building_type_usage = update_chart_layout(building_type_usage)
        
        energy_source_distribution = px.pie(dff, names='energy_source', title="Energy Source Distribution",
                                            color_discrete_sequence=px.colors.qualitative.Set3)
        energy_source_distribution = update_chart_layout(energy_source_distribution)
        
        return kpi_indicators, energy_usage_trend, energy_cost_trend, building_type_usage, energy_source_distribution    

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df=pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()