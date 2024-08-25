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
            html.H1('User Analytics Dashboard', style={
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
                        value=[df.location.unique()[0]],
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
                dbc.Col([dcc.Graph(id='followers-distribution')], width=6),
                dbc.Col([dcc.Graph(id='following-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='status-distribution')], width=6),
                dbc.Col([dcc.Graph(id='interests-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('followers-distribution', 'figure'),
         Output('following-distribution', 'figure'),
         Output('status-distribution', 'figure'),
         Output('interests-distribution', 'figure')],
        [Input('dropdown-location', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('followers-distribution', 'clickData'),
         Input('following-distribution', 'clickData'),
         Input('status-distribution', 'clickData'),
         Input('interests-distribution', 'selectedData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(locations, start_date, end_date, followers_click, following_click, status_click, interests_selection, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df[df.location.isin(locations) & 
                 (df.birthdate >= start_date) & 
                 (df.birthdate <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.location.isin(locations) & 
                         (df.birthdate >= start_date) & 
                         (df.birthdate <= end_date)]
            elif input_id == 'followers-distribution' and followers_click:
                followers_range = followers_click['points'][0]['x']
                dff = dff[(dff['followers_count'] >= followers_range[0]) & (dff['followers_count'] < followers_range[1])]
            elif input_id == 'following-distribution' and following_click:
                following_range = following_click['points'][0]['x']
                dff = dff[(dff['following_count'] >= following_range[0]) & (dff['following_count'] < following_range[1])]
            elif input_id == 'status-distribution' and status_click:
                status = status_click['points'][0]['x']
                dff = dff[dff['status'] == status]
            elif input_id == 'interests-distribution' and interests_selection:
                selected_interests = [point['x'] for point in interests_selection['points']]
                dff = dff[dff['interests'].isin(selected_interests)]

        total_users = len(dff)
        avg_followers = dff['followers_count'].mean()
        avg_following = dff['following_count'].mean()
        most_common_status = dff['status'].mode().iloc[0]
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[df.location.isin(locations) & 
                      (df.birthdate >= past_start_date) & 
                      (df.birthdate <= past_end_date)]
        
        past_total_users = len(past_dff)
        past_avg_followers = past_dff['followers_count'].mean()
        past_avg_following = past_dff['following_count'].mean()
        
        users_change = total_users - past_total_users
        followers_change = avg_followers - past_avg_followers
        following_change = avg_following - past_avg_following
        
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
            create_kpi_card('Total Users', total_users, users_change),
            create_kpi_card('Avg Followers', avg_followers, followers_change),
            create_kpi_card('Avg Following', avg_following, following_change),
            create_kpi_card('Most Common Status', most_common_status, 0)
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
        
        followers_distribution = px.histogram(dff, x='followers_count', nbins=20, title="Followers Distribution",
                                              color_discrete_sequence=[colors['primary']], labels={'followers_count': 'Followers Count'})
        followers_distribution = update_chart_layout(followers_distribution)
        
        following_distribution = px.histogram(dff, x='following_count', nbins=20, title="Following Distribution",
                                              color_discrete_sequence=[colors['primary']], labels={'following_count': 'Following Count'})
        following_distribution = update_chart_layout(following_distribution)
        
        status_distribution = px.bar(dff['status'].value_counts().reset_index(), x='index', y='status', title="User Status Distribution",
                                     color_discrete_sequence=[colors['primary']], labels={'index': 'Status', 'status': 'Count'})
        status_distribution = update_chart_layout(status_distribution)
        
        interests_distribution = px.bar(dff['interests'].value_counts().reset_index(), x='index', y='interests', title="User Interests Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'index': 'Interest', 'interests': 'Count'})
        interests_distribution = update_chart_layout(interests_distribution)
        
        return kpi_indicators, followers_distribution, following_distribution, status_distribution, interests_distribution    

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df=pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()