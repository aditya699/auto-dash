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
            html.H1('E-commerce Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Gender', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-gender',
                        options=[{'label': i, 'value': i} for i in df.gender.unique()],
                        value=[],
                        multi=True,
                        style={'width': '200px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Product Name', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-product',
                        options=[{'label': i, 'value': i} for i in df.product_name.unique()],
                        value=[],
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
                dbc.Col([dcc.Graph(id='product-sales')], width=6),
                dbc.Col([dcc.Graph(id='gender-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='sales-over-time')], width=6),
                dbc.Col([dcc.Graph(id='payment-method-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('product-sales', 'figure'),
         Output('gender-distribution', 'figure'),
         Output('sales-over-time', 'figure'),
         Output('payment-method-distribution', 'figure')],
        [Input('dropdown-gender', 'value'),
         Input('dropdown-product', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('product-sales', 'clickData'),
         Input('gender-distribution', 'clickData'),
         Input('sales-over-time', 'selectedData'),
         Input('payment-method-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(genders, products, start_date, end_date, product_click, gender_click, time_selection, payment_click, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df.copy()
        dff['purchase_date'] = pd.to_datetime(dff['purchase_date'])
        
        if genders:
            dff = dff[dff.gender.isin(genders)]
        if products:
            dff = dff[dff.product_name.isin(products)]
        dff = dff[(dff.purchase_date >= start_date) & (dff.purchase_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[(df.purchase_date >= start_date) & (df.purchase_date <= end_date)]
            elif input_id == 'product-sales' and product_click:
                product = product_click['points'][0]['x']
                dff = dff[dff['product_name'] == product]
            elif input_id == 'gender-distribution' and gender_click:
                gender = gender_click['points'][0]['label']
                dff = dff[dff['gender'] == gender]
            elif input_id == 'sales-over-time' and time_selection:
                time_range = [time_selection['range']['x'][0], time_selection['range']['x'][1]]
                dff = dff[(dff['purchase_date'] >= time_range[0]) & (dff['purchase_date'] <= time_range[1])]
            elif input_id == 'payment-method-distribution' and payment_click:
                payment_method = payment_click['points'][0]['label']
                dff = dff[dff['payment_method'] == payment_method]

        total_revenue = dff['total_price'].sum()
        total_orders = dff['order_status'].count()
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        unique_customers = dff['customer_id'].nunique()
        
        past_start_date = start_date - timedelta(days=30)
        past_end_date = end_date - timedelta(days=30)
        past_dff = df[(df.purchase_date >= past_start_date) & (df.purchase_date <= past_end_date)]
        
        past_total_revenue = past_dff['total_price'].sum()
        past_total_orders = past_dff['order_status'].count()
        past_average_order_value = past_total_revenue / past_total_orders if past_total_orders > 0 else 0
        past_unique_customers = past_dff['customer_id'].nunique()
        
        revenue_change = total_revenue - past_total_revenue
        orders_change = total_orders - past_total_orders
        aov_change = average_order_value - past_average_order_value
        customers_change = unique_customers - past_unique_customers
        
        def create_kpi_card(title, value, change):
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400'}),
                html.Div([
                    html.Span(f'{value:,.2f}', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                    html.Div([
                        html.Span('▲' if change > 0 else '▼', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px'}),
                        html.Span(f'{abs(change):,.2f}', 
                                  style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '18px', 'marginLeft': '5px'})
                    ], style={'marginTop': '5px'})
                ])
            ], style=kpi_style)
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Revenue', total_revenue, revenue_change),
            create_kpi_card('Total Orders', total_orders, orders_change),
            create_kpi_card('Avg Order Value', average_order_value, aov_change),
            create_kpi_card('Unique Customers', unique_customers, customers_change)
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
        
        product_sales = px.bar(dff.groupby('product_name')['total_price'].sum().reset_index().sort_values('total_price', ascending=False).head(10), 
                               x='product_name', y='total_price', title="Top 10 Product Sales",
                               color_discrete_sequence=[colors['primary']], labels={'product_name': 'Product Name', 'total_price': 'Total Sales'})
        product_sales = update_chart_layout(product_sales)
        
        gender_distribution = px.pie(dff, names='gender', values='total_price', title="Sales Distribution by Gender",
                                     color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent']])
        gender_distribution = update_chart_layout(gender_distribution)
        
        sales_over_time = px.line(dff.groupby('purchase_date')['total_price'].sum().reset_index(), x='purchase_date', y='total_price', 
                                  title="Sales Over Time", color_discrete_sequence=[colors['primary']])
        sales_over_time = update_chart_layout(sales_over_time)
        
        payment_method_distribution = px.pie(dff, names='payment_method', values='total_price', title="Sales by Payment Method",
                                             color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent'], colors['negative']])
        payment_method_distribution = update_chart_layout(payment_method_distribution)
        
        return kpi_indicators, product_sales, gender_distribution, sales_over_time, payment_method_distribution

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()