import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
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
            html.H1('Sustainability Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Renewable Energy Source', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-energy-source',
                        options=[{'label': i, 'value': i} for i in df.renewable_energy_source.unique()],
                        value=df.renewable_energy_source.unique().tolist(),
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Environmental Certification', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-certification',
                        options=[{'label': i, 'value': i} for i in df.environmental_certification.unique()],
                        value=df.environmental_certification.unique().tolist(),
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
                dbc.Col([dcc.Graph(id='carbon-footprint')], width=6),
                dbc.Col([dcc.Graph(id='energy-consumption')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='waste-generated')], width=6),
                dbc.Col([dcc.Graph(id='water-usage')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('carbon-footprint', 'figure'),
         Output('energy-consumption', 'figure'),
         Output('waste-generated', 'figure'),
         Output('water-usage', 'figure')],
        [Input('dropdown-energy-source', 'value'),
         Input('dropdown-certification', 'value'),
         Input('carbon-footprint', 'clickData'),
         Input('energy-consumption', 'clickData'),
         Input('waste-generated', 'clickData'),
         Input('water-usage', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(energy_sources, certifications, carbon_click, energy_click, waste_click, water_click, reset_clicks):
        dff = df[df.renewable_energy_source.isin(energy_sources) & 
                 df.environmental_certification.isin(certifications)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.renewable_energy_source.isin(energy_sources) & 
                         df.environmental_certification.isin(certifications)]
        
        avg_sustainability_score = dff['sustainability_score'].mean()
        avg_recycling_rate = dff['recycling_rate'].mean()
        avg_greenhouse_gas = dff['greenhouse_gas_emissions'].mean()
        tree_planting_percentage = (dff['tree_planting_initiative'].sum() / len(dff)) * 100
        
        def create_kpi_card(title, value, unit=''):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:.2f}{unit}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Avg Sustainability Score', avg_sustainability_score),
            create_kpi_card('Avg Recycling Rate', avg_recycling_rate, '%'),
            create_kpi_card('Avg Greenhouse Gas Emissions', avg_greenhouse_gas, ' tons'),
            create_kpi_card('Tree Planting Initiative', tree_planting_percentage, '%')
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
        
        carbon_footprint = px.scatter(dff, x='energy_consumption', y='carbon_footprint', 
                                      color='renewable_energy_source', size='sustainability_score',
                                      title="Carbon Footprint vs Energy Consumption",
                                      labels={'energy_consumption': 'Energy Consumption', 'carbon_footprint': 'Carbon Footprint'})
        carbon_footprint = update_chart_layout(carbon_footprint)
        
        energy_consumption = px.bar(dff, x='renewable_energy_source', y='energy_consumption', 
                                    color='environmental_certification', title="Energy Consumption by Source",
                                    labels={'renewable_energy_source': 'Energy Source', 'energy_consumption': 'Energy Consumption'})
        energy_consumption = update_chart_layout(energy_consumption)
        
        waste_generated = px.scatter(dff, x='recycling_rate', y='waste_generated', 
                                     color='environmental_certification', size='sustainability_score',
                                     title="Waste Generated vs Recycling Rate",
                                     labels={'recycling_rate': 'Recycling Rate', 'waste_generated': 'Waste Generated'})
        waste_generated = update_chart_layout(waste_generated)
        
        water_usage = px.box(dff, x='environmental_certification', y='water_usage', 
                             color='renewable_energy_source', title="Water Usage by Certification",
                             labels={'environmental_certification': 'Environmental Certification', 'water_usage': 'Water Usage'})
        water_usage = update_chart_layout(water_usage)
        
        return kpi_indicators, carbon_footprint, energy_consumption, waste_generated, water_usage

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()