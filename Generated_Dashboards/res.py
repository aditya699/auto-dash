import os
from dash import Dash, html, dcc, callback, Output, Input, ctx, ALL
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['delivery_date'] = pd.to_datetime(df['delivery_date'])
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
            html.H1('Inventory Dashboard', style={
                'textAlign': 'center', 
                'color': colors['text'], 
                'marginBottom': '30px', 
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Supplier', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-supplier',
                        options=[{'label': 'Select All', 'value': 'all'}] + [{'label': i, 'value': i} for i in df.supplier_name.unique()],
                        value=['all'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['delivery_date'].min(),
                        end_date=df['delivery_date'].max(),
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
                dbc.Col([dcc.Graph(id='product-quantity')], width=6),
                dbc.Col([dcc.Graph(id='profit-margin')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='supplier-performance')], width=6),
                dbc.Col([dcc.Graph(id='warehouse-distribution')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px', 
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('product-quantity', 'figure'),
         Output('profit-margin', 'figure'),
         Output('supplier-performance', 'figure'),
         Output('warehouse-distribution', 'figure')],
        [Input('dropdown-supplier', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('product-quantity', 'clickData'),
         Input('profit-margin', 'clickData'),
         Input('supplier-performance', 'clickData'),
         Input('warehouse-distribution', 'clickData'),
         Input('reset-button', 'n_clicks')]
    )
    def update_dashboard(suppliers, start_date, end_date, product_click, profit_click, supplier_click, warehouse_click, reset_clicks):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        if 'all' in suppliers:
            dff = df
        else:
            dff = df[df.supplier_name.isin(suppliers)]
        
        dff = dff[(dff.delivery_date >= start_date) & (dff.delivery_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                dff = df[(df.delivery_date >= start_date) & (df.delivery_date <= end_date)]
            elif input_id == 'product-quantity' and product_click:
                product = product_click['points'][0]['x']
                dff = dff[dff['product_name'] == product]
            elif input_id == 'profit-margin' and profit_click:
                product = profit_click['points'][0]['x']
                dff = dff[dff['product_name'] == product]
            elif input_id == 'supplier-performance' and supplier_click:
                supplier = supplier_click['points'][0]['x']
                dff = dff[dff['supplier_name'] == supplier]
            elif input_id == 'warehouse-distribution' and warehouse_click:
                warehouse = warehouse_click['points'][0]['label']
                dff = dff[dff['warehouse_location'] == warehouse]

        total_quantity = dff['quantity'].sum()
        total_profit = (dff['sale_price'] - dff['purchase_price']).sum()
        avg_profit_margin = dff['profit_margin'].mean()
        unique_products = dff['product_name'].nunique()
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.delivery_date >= past_start_date) & (df.delivery_date <= past_end_date)]
        
        past_total_quantity = past_dff['quantity'].sum()
        past_total_profit = (past_dff['sale_price'] - past_dff['purchase_price']).sum()
        past_avg_profit_margin = past_dff['profit_margin'].mean()
        past_unique_products = past_dff['product_name'].nunique()
        
        quantity_change = total_quantity - past_total_quantity
        profit_change = total_profit - past_total_profit
        margin_change = avg_profit_margin - past_avg_profit_margin
        products_change = unique_products - past_unique_products
        
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
            create_kpi_card('Total Quantity', total_quantity, quantity_change),
            create_kpi_card('Total Profit', total_profit, profit_change),
            create_kpi_card('Avg Profit Margin', avg_profit_margin, margin_change),
            create_kpi_card('Unique Products', unique_products, products_change)
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
        
        product_quantity = px.bar(dff, x='product_name', y='quantity', title="Product Quantity Analysis",
                                   color_discrete_sequence=[colors['primary']], labels={'product_name': 'Product Name', 'quantity': 'Quantity'})
        product_quantity = update_chart_layout(product_quantity)
        
        profit_margin = px.bar(dff, x='product_name', y='profit_margin', title="Product Profit Margin Analysis",
                               color_discrete_sequence=[colors['primary']], labels={'product_name':'Product Name','profit_margin':'Profit Margin'})
        profit_margin = update_chart_layout(profit_margin)
        
        supplier_performance = px.bar(dff, x='supplier_name', y='quantity', title="Supplier Performance",
                                       color_discrete_sequence=[colors['primary']], labels={'supplier_name':'Supplier Name','quantity':'Quantity'})
        supplier_performance = update_chart_layout(supplier_performance)
        
        warehouse_distribution = px.pie(dff, names='warehouse_location', values='quantity', title="Warehouse Distribution",
                                        color_discrete_sequence=px.colors.qualitative.Set3, labels={'warehouse_location':'Warehouse','quantity':'Quantity'})
        warehouse_distribution = update_chart_layout(warehouse_distribution)
        
        return kpi_indicators, product_quantity, profit_margin, supplier_performance, warehouse_distribution    

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df=pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()