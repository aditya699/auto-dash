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
                        value=[df.location.unique()[0]],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Status', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-status',
                        options=[{'label': i, 'value': i} for i in df.status.unique()],
                        value=[df.status.unique()[0]],
                        multi=True,
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
                dbc.Col([dcc.Graph(id='age-distribution')], width=6),
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
         Output('age-distribution', 'figure'),
         Output('interests-distribution', 'figure')],
        [Input('dropdown-location', 'value'),
         Input('dropdown-status', 'value'),
         Input('followers-distribution', 'clickData'),
         Input('following-distribution', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('interests-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(locations, statuses, followers_click, following_click, age_selection, interests_click, reset_clicks):
        dff = df[df.location.isin(locations) & df.status.isin(statuses)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.location.isin(locations) & df.status.isin(statuses)]
            elif input_id == 'followers-distribution' and followers_click:
                followers_range = followers_click['points'][0]['x'].split('-')
                dff = dff[(dff['followers_count'] >= int(followers_range[0])) & (dff['followers_count'] < int(followers_range[1]))]
            elif input_id == 'following-distribution' and following_click:
                following_range = following_click['points'][0]['x'].split('-')
                dff = dff[(dff['following_count'] >= int(following_range[0])) & (dff['following_count'] < int(following_range[1]))]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['age'] >= age_range[0]) & (dff['age'] <= age_range[1])]
            elif input_id == 'interests-distribution' and interests_click:
                interest = interests_click['points'][0]['x']
                dff = dff[dff['interests'].str.contains(interest)]

        total_users = len(dff)
        avg_followers = dff['followers_count'].mean()
        avg_following = dff['following_count'].mean()
        avg_age = (datetime.now() - dff['birthdate']).mean().days / 365.25

        def create_kpi_card(title, value, change=None):
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
            create_kpi_card('Avg Age', avg_age)
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

        age_distribution = px.histogram(dff, x='birthdate', nbins=20, title="Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'birthdate': 'Age'})
        age_distribution = update_chart_layout(age_distribution)

        interests_distribution = px.bar(dff['interests'].str.split(',', expand=True).melt().value.value_counts().reset_index(),
                                        x='index', y='value', title="Interests Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'index': 'Interest', 'value': 'Count'})
        interests_distribution = update_chart_layout(interests_distribution)

        return kpi_indicators, followers_distribution, following_distribution, age_distribution, interests_distribution

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()