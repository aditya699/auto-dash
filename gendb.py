import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['retirement_savings_balance'] = pd.to_numeric(df['retirement_savings_balance'], errors='coerce')
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
            html.H1('Financial Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Income Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.RangeSlider(
                        id='income-range-slider',
                        min=df['income'].min(),
                        max=df['income'].max(),
                        step=1000,
                        marks={int(df['income'].min()): f'${int(df["income"].min())}', int(df['income'].max()): f'${int(df["income"].max())}'},
                        value=[df['income'].min(), df['income'].max()]
                    )
                ], style={'width': '300px'}),
                html.Div([
                    html.Label('Credit Score Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.RangeSlider(
                        id='credit-score-range-slider',
                        min=df['credit_score'].min(),
                        max=df['credit_score'].max(),
                        step=10,
                        marks={int(df['credit_score'].min()): str(int(df['credit_score'].min())), int(df['credit_score'].max()): str(int(df['credit_score'].max()))},
                        value=[df['credit_score'].min(), df['credit_score'].max()]
                    )
                ], style={'width': '300px'}),
                html.Div([
                    html.Button('Reset Filters', id='reset-button', n_clicks=0, 
                                style={'padding': '10px 20px', 'backgroundColor': colors['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'all 0.3s ease'})
                ])
            ], style=filter_style),
            
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='income-expenses-scatter')], width=6),
                dbc.Col([dcc.Graph(id='savings-investment-scatter')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='loan-interest-histogram')], width=6),
                dbc.Col([dcc.Graph(id='retirement-savings-histogram')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('income-expenses-scatter', 'figure'),
         Output('savings-investment-scatter', 'figure'),
         Output('loan-interest-histogram', 'figure'),
         Output('retirement-savings-histogram', 'figure'),
         Output('income-range-slider', 'value'),
         Output('credit-score-range-slider', 'value')],
        [Input('income-range-slider', 'value'),
         Input('credit-score-range-slider', 'value'),
         Input('income-expenses-scatter', 'selectedData'),
         Input('savings-investment-scatter', 'selectedData'),
         Input('loan-interest-histogram', 'selectedData'),
         Input('retirement-savings-histogram', 'selectedData'),
         Input('reset-button', 'n_clicks')],
        [State('income-range-slider', 'min'),
         State('income-range-slider', 'max'),
         State('credit-score-range-slider', 'min'),
         State('credit-score-range-slider', 'max')]
    )
    def update_dashboard(income_range, credit_score_range, income_expenses_selection, savings_investment_selection, 
                         loan_interest_selection, retirement_savings_selection, reset_clicks, 
                         income_min, income_max, credit_score_min, credit_score_max):
        dff = df[(df['income'] >= income_range[0]) & (df['income'] <= income_range[1]) &
                 (df['credit_score'] >= credit_score_range[0]) & (df['credit_score'] <= credit_score_range[1])]
        
        if ctx.triggered_id == 'reset-button':
            dff = df
            income_range = [income_min, income_max]
            credit_score_range = [credit_score_min, credit_score_max]
        elif ctx.triggered_id == 'income-expenses-scatter' and income_expenses_selection:
            points = income_expenses_selection['points']
            dff = dff[dff['user_id'].isin([p['customdata'][0] for p in points])]
        elif ctx.triggered_id == 'savings-investment-scatter' and savings_investment_selection:
            points = savings_investment_selection['points']
            dff = dff[dff['user_id'].isin([p['customdata'][0] for p in points])]
        elif ctx.triggered_id == 'loan-interest-histogram' and loan_interest_selection:
            selected_bins = loan_interest_selection['points']
            min_rate = min(point['x'] for point in selected_bins)
            max_rate = max(point['x'] for point in selected_bins)
            dff = dff[(dff['loan_interest_rate'] >= min_rate) & (dff['loan_interest_rate'] <= max_rate)]
        elif ctx.triggered_id == 'retirement-savings-histogram' and retirement_savings_selection:
            selected_bins = retirement_savings_selection['points']
            min_savings = min(point['x'] for point in selected_bins)
            max_savings = max(point['x'] for point in selected_bins)
            dff = dff[(dff['retirement_savings_balance'] >= min_savings) & (dff['retirement_savings_balance'] <= max_savings)]

        avg_income = dff['income'].mean()
        avg_expenses = dff['expenses'].mean()
        avg_savings = dff['savings'].mean()
        avg_investment = dff['investment_portfolio_value'].mean()
        
        past_dff = df[(df['income'] >= income_range[0]) & (df['income'] <= income_range[1]) &
                      (df['credit_score'] >= credit_score_range[0]) & (df['credit_score'] <= credit_score_range[1])]
        
        past_avg_income = past_dff['income'].mean()
        past_avg_expenses = past_dff['expenses'].mean()
        past_avg_savings = past_dff['savings'].mean()
        past_avg_investment = past_dff['investment_portfolio_value'].mean()
        
        income_change = avg_income - past_avg_income
        expenses_change = avg_expenses - past_avg_expenses
        savings_change = avg_savings - past_avg_savings
        investment_change = avg_investment - past_avg_investment
        
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'${value:,.0f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'${abs(change):,.0f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Avg Income', avg_income, income_change),
            create_kpi_card('Avg Expenses', avg_expenses, expenses_change),
            create_kpi_card('Avg Savings', avg_savings, savings_change),
            create_kpi_card('Avg Investment', avg_investment, investment_change)
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
        
        income_expenses_scatter = px.scatter(dff, x='income', y='expenses', title="Income vs Expenses",
                                             color='credit_score', size='savings', hover_data=['user_id'],
                                             labels={'income': 'Income', 'expenses': 'Expenses', 'credit_score': 'Credit Score'})
        income_expenses_scatter = update_chart_layout(income_expenses_scatter)
        
        savings_investment_scatter = px.scatter(dff, x='savings', y='investment_portfolio_value', title="Savings vs Investment",
                                                color='credit_score', size='income', hover_data=['user_id'],
                                                labels={'savings': 'Savings', 'investment_portfolio_value': 'Investment Portfolio Value', 'credit_score': 'Credit Score'})
        savings_investment_scatter = update_chart_layout(savings_investment_scatter)
        
        loan_interest_histogram = px.histogram(dff, x='loan_interest_rate', title="Loan Interest Rate Distribution",
                                               color_discrete_sequence=[colors['primary']], labels={'loan_interest_rate': 'Loan Interest Rate'})
        loan_interest_histogram = update_chart_layout(loan_interest_histogram)
        
        retirement_savings_histogram = px.histogram(dff, x='retirement_savings_balance', title="Retirement Savings Distribution",
                                                    color_discrete_sequence=[colors['primary']], labels={'retirement_savings_balance': 'Retirement Savings Balance'})
        retirement_savings_histogram = update_chart_layout(retirement_savings_histogram)
        
        return kpi_indicators, income_expenses_scatter, savings_investment_scatter, loan_interest_histogram, retirement_savings_histogram, income_range, credit_score_range

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()