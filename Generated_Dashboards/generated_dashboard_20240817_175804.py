import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
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
            html.H1('Sales Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Country', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-country',
                        options=[{'label': i, 'value': i} for i in df.country.unique()],
                        value=['France'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['purchase_date'].min(),
                        end_date=df['purchase_date'].max(),
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
                dbc.Col([dcc.Graph(id='customer-purchase')], width=6),
                dbc.Col([dcc.Graph(id='product-sales')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='sales-rep-performance')], width=6),
                dbc.Col([dcc.Graph(id='age-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('customer-purchase', 'figure'),
         Output('product-sales', 'figure'),
         Output('sales-rep-performance', 'figure'),
         Output('age-distribution', 'figure')],
        [Input('dropdown-country', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('customer-purchase', 'clickData'),
         Input('product-sales', 'clickData'),
         Input('sales-rep-performance', 'clickData'),
         Input('age-distribution', 'selectedData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(countries, start_date, end_date, customer_click, product_click, sales_rep_click, age_selection, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df[df.country.isin(countries) & 
                 (df.purchase_date >= start_date) & 
                 (df.purchase_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[df.country.isin(countries) & 
                         (df.purchase_date >= start_date) & 
                         (df.purchase_date <= end_date)]
            elif input_id == 'customer-purchase' and customer_click:
                customer = customer_click['points'][0]['x']
                dff = dff[dff['customer_name'] == customer]
            elif input_id == 'product-sales' and product_click:
                product = product_click['points'][0]['x']
                dff = dff[dff['product_name'] == product]
            elif input_id == 'sales-rep-performance' and sales_rep_click:
                sales_rep = sales_rep_click['points'][0]['x']
                dff = dff[dff['sales_representative'] == sales_rep]
            elif input_id == 'age-distribution' and age_selection:
                age_range = [age_selection['range']['x'][0], age_selection['range']['x'][1]]
                dff = dff[(dff['age'] >= age_range[0]) & (dff['age'] <= age_range[1])]

        
        total_revenue = dff['purchase_amount'].sum()
        total_customers = dff['customer_id'].nunique()
        average_order_value = dff['purchase_amount'].mean()
        total_orders = dff['purchase_date'].count()
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[df.country.isin(countries) & 
                      (df.purchase_date >= past_start_date) & 
                      (df.purchase_date <= past_end_date)]
        
        past_total_revenue = past_dff['purchase_amount'].sum()
        past_total_customers = past_dff['customer_id'].nunique()
        past_average_order_value = past_dff['purchase_amount'].mean()
        past_total_orders = past_dff['purchase_date'].count()
        
        revenue_change = total_revenue - past_total_revenue
        customers_change = total_customers - past_total_customers
        aov_change = average_order_value - past_average_order_value
        orders_change = total_orders - past_total_orders
        
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
            create_kpi_card('Total Revenue', total_revenue, revenue_change),
            create_kpi_card('Total Customers', total_customers, customers_change),
            create_kpi_card('Avg Order Value', average_order_value, aov_change),
            create_kpi_card('Total Orders', total_orders, orders_change)
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
        
        customer_purchase = px.bar(dff, x='customer_name', y='purchase_amount', title="Customer Purchase Analysis",
                                   color_discrete_sequence=[colors['primary']], labels={'customer_name': 'Customer Name', 'purchase_amount': 'Purchase Amount'})
        customer_purchase = update_chart_layout(customer_purchase)
        
        product_sales = px.bar(dff, x='product_name', y='purchase_amount', title="Product Sales Analysis",
                               color_discrete_sequence=[colors['primary']], labels={'product_name':'Product Name','purchase_amount':'Purchase amount'})
        product_sales = update_chart_layout(product_sales)
        
        sales_rep_performance = px.bar(dff, x='sales_representative', y='purchase_amount', title="Sales Representative Performance",
                                       color_discrete_sequence=[colors['primary']], labels={'sales_representative':'Sales Representative','purchase_amount':'Purchase Amount'})
        sales_rep_performance = update_chart_layout(sales_rep_performance)
        
        age_distribution = px.histogram(dff, x='age', nbins=10, title="Customer Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'age':'Age'})
        age_distribution = update_chart_layout(age_distribution)
        
        return kpi_indicators, customer_purchase, product_sales, sales_rep_performance, age_distribution    

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df=pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()