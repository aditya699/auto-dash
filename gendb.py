import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
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
            'background': '#023020',
            'text': '#AA336A',
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
                    html.Label('Store Location', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-store',
                        options=[{'label': 'Select All', 'value': 'all'}] + [{'label': i, 'value': i} for i in df.store_location.unique()],
                        value=['all'],
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
                dbc.Col([dcc.Graph(id='store-performance')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='payment-method-distribution')], width=6),
                dbc.Col([dcc.Graph(id='sales-trend')], width=6),
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
         Output('store-performance', 'figure'),
         Output('payment-method-distribution', 'figure'),
         Output('sales-trend', 'figure'),
         Output('dropdown-store', 'value'),
         Output('date-picker-range', 'start_date'),
         Output('date-picker-range', 'end_date')],
        [Input('dropdown-store', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('product-sales', 'clickData'),
         Input('store-performance', 'clickData'),
         Input('payment-method-distribution', 'clickData'),
         Input('sales-trend', 'selectedData'),
         Input('reset-button', 'n_clicks')],
        [State('dropdown-store', 'options')]
    )
    def update_dashboard(stores, start_date, end_date, product_click, store_click, payment_click, sales_selection, reset_clicks, store_options):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if 'all' in stores:
            stores = [option['value'] for option in store_options if option['value'] != 'all']
        
        dff = df[df.store_location.isin(stores) & 
                 (df.purchase_date >= start_date) & 
                 (df.purchase_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                stores = ['all']
                start_date = df['purchase_date'].min()
                end_date = df['purchase_date'].max()
                dff = df
            elif input_id == 'product-sales' and product_click:
                product = product_click['points'][0]['x']
                dff = dff[dff['product_id'] == product]
            elif input_id == 'store-performance' and store_click:
                store = store_click['points'][0]['x']
                dff = dff[dff['store_location'] == store]
            elif input_id == 'payment-method-distribution' and payment_click:
                payment_method = payment_click['points'][0]['label']
                dff = dff[dff['payment_method'] == payment_method]
            elif input_id == 'sales-trend' and sales_selection:
                date_range = [sales_selection['range']['x'][0], sales_selection['range']['x'][1]]
                dff = dff[(dff['purchase_date'] >= date_range[0]) & (dff['purchase_date'] <= date_range[1])]

        total_revenue = dff['total_price'].sum()
        total_transactions = dff['transaction_id'].nunique()
        average_order_value = dff['total_price'].mean()
        total_quantity = dff['quantity'].sum()
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[df.store_location.isin(stores) & 
                      (df.purchase_date >= past_start_date) & 
                      (df.purchase_date <= past_end_date)]
        
        past_total_revenue = past_dff['total_price'].sum()
        past_total_transactions = past_dff['transaction_id'].nunique()
        past_average_order_value = past_dff['total_price'].mean()
        past_total_quantity = past_dff['quantity'].sum()
        
        revenue_change = total_revenue - past_total_revenue
        transactions_change = total_transactions - past_total_transactions
        aov_change = average_order_value - past_average_order_value
        quantity_change = total_quantity - past_total_quantity
        
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
            create_kpi_card('Total Transactions', total_transactions, transactions_change),
            create_kpi_card('Avg Order Value', average_order_value, aov_change),
            create_kpi_card('Total Quantity', total_quantity, quantity_change)
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
        
        product_sales = px.bar(dff, x='product_id', y='total_price', title="Product Sales Analysis",
                               color_discrete_sequence=[colors['primary']], labels={'product_id': 'Product ID', 'total_price': 'Total Sales'})
        product_sales = update_chart_layout(product_sales)
        
        store_performance = px.bar(dff, x='store_location', y='total_price', title="Store Performance",
                                   color_discrete_sequence=[colors['primary']], labels={'store_location':'Store Location','total_price':'Total Sales'})
        store_performance = update_chart_layout(store_performance)
        
        payment_method_distribution = px.pie(dff, names='payment_method', values='total_price', title="Payment Method Distribution",
                                             color_discrete_sequence=px.colors.qualitative.Set3, labels={'payment_method':'Payment Method','total_price':'Total Sales'})
        payment_method_distribution = update_chart_layout(payment_method_distribution)
        
        sales_trend = px.line(dff.groupby('purchase_date')['total_price'].sum().reset_index(), 
                              x='purchase_date', y='total_price', title="Daily Sales Trend",
                              color_discrete_sequence=[colors['primary']], labels={'purchase_date':'Date','total_price':'Total Sales'})
        sales_trend = update_chart_layout(sales_trend)
        
        return kpi_indicators, product_sales, store_performance, payment_method_distribution, sales_trend, stores, start_date, end_date

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df=pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()