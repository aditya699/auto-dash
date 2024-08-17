import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['birthdate'] = pd.to_datetime(df['birthdate'])
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
            html.H1('User Profile Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Location', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-location',
                        options=[{'label': i, 'value': i} for i in df.location.unique()],
                        value=[df.location.iloc[0]],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Status', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-status',
                        options=[{'label': i, 'value': i} for i in df.status.unique()],
                        value=[df.status.iloc[0]],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['birthdate'].min(),
                        end_date=df['birthdate'].max(),
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
                dbc.Col([dcc.Graph(id='followers-following')], width=6),
                dbc.Col([dcc.Graph(id='age-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='location-distribution')], width=6),
                dbc.Col([dcc.Graph(id='status-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('followers-following', 'figure'),
         Output('age-distribution', 'figure'),
         Output('location-distribution', 'figure'),
         Output('status-distribution', 'figure')],
        [Input('dropdown-location', 'value'),
         Input('dropdown-status', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('followers-following', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('location-distribution', 'clickData'),
         Input('status-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(locations, statuses, start_date, end_date, followers_click, age_selection, location_click, status_click, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df[df.location.isin(locations) & 
                 df.status.isin(statuses) & 
                 (df.birthdate >= start_date) & 
                 (df.birthdate <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.location.isin(locations) & 
                         df.status.isin(statuses) & 
                         (df.birthdate >= start_date) & 
                         (df.birthdate <= end_date)]
            elif input_id == 'followers-following' and followers_click:
                username = followers_click['points'][0]['x']
                dff = dff[dff['username'] == username]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['birthdate'].dt.year.max() - dff['birthdate'].dt.year >= age_range[0]) & 
                          (dff['birthdate'].dt.year.max() - dff['birthdate'].dt.year <= age_range[1])]
            elif input_id == 'location-distribution' and location_click:
                location = location_click['points'][0]['x']
                dff = dff[dff['location'] == location]
            elif input_id == 'status-distribution' and status_click:
                status = status_click['points'][0]['x']
                dff = dff[dff['status'] == status]

        total_users = len(dff)
        avg_followers = dff['followers_count'].mean()
        avg_following = dff['following_count'].mean()
        active_users = dff[dff['status'] == 'active'].shape[0]
        
        def create_kpi_card(title, value):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Users', total_users),
            create_kpi_card('Avg Followers', avg_followers),
            create_kpi_card('Avg Following', avg_following),
            create_kpi_card('Active Users', active_users)
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
        
        followers_following = px.scatter(dff, x='followers_count', y='following_count', hover_data=['username'], title="Followers vs Following",
                                         color_discrete_sequence=[colors['primary']], labels={'followers_count': 'Followers', 'following_count': 'Following'})
        followers_following = update_chart_layout(followers_following)
        
        dff['age'] = datetime.now().year - dff['birthdate'].dt.year
        age_distribution = px.histogram(dff, x='age', nbins=20, title="Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'age':'Age'})
        age_distribution = update_chart_layout(age_distribution)
        
        location_distribution = px.bar(dff['location'].value_counts().reset_index(), x='location', y='count', title="Location Distribution",
                                       color_discrete_sequence=[colors['primary']], labels={'location':'Location', 'count':'Count'})
        location_distribution = update_chart_layout(location_distribution)
        
        status_distribution = px.pie(dff, names='status', title="Status Distribution",
                                     color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent']])
        status_distribution = update_chart_layout(status_distribution)
        
        return kpi_indicators, followers_following, age_distribution, location_distribution, status_distribution

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()