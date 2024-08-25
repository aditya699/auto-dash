# Import necessary libraries
import os
from dash import Dash, html, dcc, callback, Output, Input, ctx
import plotly.express as px
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

# Load environment variables from .env file
load_dotenv()

def load_data():
    while True:
        try:
            n = "sales_data_1.csv"
            df = pd.read_csv(n)
            df['purchase_date'] = pd.to_datetime(df['purchase_date'])
            return df
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

def create_app(df):
    # Initialize the Dash app
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Define color scheme for consistent styling
    colors = {
        'background': '#F7F7F7',  # Light gray background
        'text': '#333333',        # Dark gray text
        'primary': '#3498DB',     # Bright blue for primary elements
        'secondary': '#2ECC71',   # Green for secondary elements (positive changes)
        'accent': '#F39C12',      # Orange for accents
        'negative': '#E74C3C'     # Red for negative changes (used sparingly)
    }

    kpi_style = {
    'textAlign': 'center',
    'padding': '15px',
    'backgroundColor': 'white',
    'borderRadius': '10px',
    'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
    'margin': '10px',
    'width': '220px',  # Increased width slightly
    'height': '150px',  # Fixed height for all cards
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'space-between',
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

    # Update the dropdown options to include 'Select All'
    country_options = [{'label': 'Select All', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df.country.unique()]

    # Layout of the dashboard
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
            
            # Filter section
            html.Div([
                html.Div([
                    html.Label('Country', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-country',
                        options=country_options,
                        value=['ALL'],  # Default value as a list with 'ALL' selected
                        multi=True,  # Enable multi-select
                        style={'width': '300px'}  # Increased width to accommodate multiple selections
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
            
            # KPI indicators section
            html.Div(id='kpi-indicators', style={'margin': '30px 0'}),
            
            # Charts section
            dbc.Row([
                dbc.Col([dcc.Graph(id='time-series-chart')], width=12),

            ],className='mb-4'),

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

    # Callback function for updating the dashboard
    @callback(
        [Output('kpi-indicators', 'children'),
         Output('time-series-chart', 'figure'),
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
        # Convert string dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Handle 'Select All' option
        if 'ALL' in countries:
            dff = df
        else:
            dff = df[df.country.isin(countries)]
        
        # Filter the dataframe based on selected date range
        dff = dff[(dff.purchase_date >= start_date) & (dff.purchase_date <= end_date)]
        
        # Apply cross-filtering based on chart interactions
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                # Reset all filters
                dff = df[(df.purchase_date >= start_date) & (df.purchase_date <= end_date)]
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

        
        # Calculate KPI values for the selected period
        total_revenue = dff['purchase_amount'].sum()
        total_customers = dff['customer_id'].nunique()
        average_order_value = dff['purchase_amount'].mean()
        total_orders = dff['purchase_date'].count()
        
        # Calculate KPI values for 6 months ago
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.purchase_date >= past_start_date) & (df.purchase_date <= past_end_date)]
        
        past_total_revenue = past_dff['purchase_amount'].sum()
        past_total_customers = past_dff['customer_id'].nunique()
        past_average_order_value = past_dff['purchase_amount'].mean()
        past_total_orders = past_dff['purchase_date'].count()
        
        # Calculate changes
        revenue_change = total_revenue - past_total_revenue
        customers_change = total_customers - past_total_customers
        aov_change = average_order_value - past_average_order_value
        orders_change = total_orders - past_total_orders
        
        def create_kpi_card(title, current_value, previous_value):
            change = current_value - previous_value
            change_percentage = (change / previous_value) * 100 if previous_value != 0 else 0
            return html.Div([
                html.H3(title, style={'color': colors['text'], 'marginBottom': '10px', 'fontSize': '16px', 'fontWeight': '400', 'height': '20px'}),
                html.Div([
                    html.Span(f'{current_value:,.0f}', style={'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['primary']}),
                ], style={'height': '30px'}),
                html.Div([
                    html.Span(f'Previous: {previous_value:,.0f}', style={'fontSize': '14px', 'color': colors['text']}),
                ], style={'height': '20px'}),
                html.Div([
                    html.Div([
                        html.Span(f'{"▲" if change > 0 else "▼"}', 
                                style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '16px', 'marginRight': '5px'}),
                        html.Span(f'{abs(change):,.0f} ({abs(change_percentage):.1f}%)', 
                                style={'color': colors['secondary'] if change > 0 else colors['negative'], 'fontSize': '14px'})
                    ], style={'display': 'inline-block'})
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '20px'})
            ], style=kpi_style)

                
       # In the update_dashboard function:
        kpi_indicators = html.Div([
            create_kpi_card('Total Revenue', total_revenue, past_total_revenue),
            create_kpi_card('Total Customers', total_customers, past_total_customers),
            create_kpi_card('Avg Order Value', average_order_value, past_average_order_value),
            create_kpi_card('Total Orders', total_orders, past_total_orders)
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'stretch', 'flexWrap': 'wrap'})
        
        # Function to update chart layout
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
                clickmode='event+select',
                  hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Rockwell"
                )
            )
            fig.update_xaxes(showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            return fig
        
        # Create graphs with interactivity
        time_series = px.line(dff.groupby('purchase_date')['purchase_amount'].sum().reset_index(), 
                              x='purchase_date', y='purchase_amount', 
                              title="Daily Sales Over Time",
                              labels={'purchase_date': 'Date', 'purchase_amount': 'Total Sales'})
        time_series.update_traces(mode='lines+markers', hovertemplate='Date: %{x}<br>Sales: $%{y:,.2f}')
        time_series = update_chart_layout(time_series)

        # Create graphs with interactivity and improved tooltips
        customer_purchase = px.bar(dff.groupby('customer_name')['purchase_amount'].sum().reset_index().sort_values('purchase_amount', ascending=False).head(10), 
                                   x='customer_name', y='purchase_amount', title="Top 10 Customers by Purchase Amount",
                                   color_discrete_sequence=[colors['primary']], 
                                   labels={'customer_name': 'Customer Name', 'purchase_amount': 'Purchase Amount'})
        customer_purchase.update_traces(hovertemplate='Customer: %{x}<br>Total Purchase: $%{y:,.2f}')
        customer_purchase = update_chart_layout(customer_purchase)
        
        product_sales = px.bar(dff.groupby('product_name')['purchase_amount'].sum().reset_index().sort_values('purchase_amount', ascending=False).head(10), 
                               x='product_name', y='purchase_amount', title="Top 10 Products by Sales",
                               color_discrete_sequence=[colors['primary']], 
                               labels={'product_name':'Product Name','purchase_amount':'Sales Amount'})
        product_sales.update_traces(hovertemplate='Product: %{x}<br>Total Sales: $%{y:,.2f}')
        product_sales = update_chart_layout(product_sales)
        
        sales_rep_performance = px.bar(dff.groupby('sales_representative')['purchase_amount'].sum().reset_index().sort_values('purchase_amount', ascending=False), 
                                       x='sales_representative', y='purchase_amount', title="Sales Representative Performance",
                                       color_discrete_sequence=[colors['primary']], 
                                       labels={'sales_representative':'Sales Representative','purchase_amount':'Total Sales'})
        sales_rep_performance.update_traces(hovertemplate='Sales Rep: %{x}<br>Total Sales: $%{y:,.2f}')
        sales_rep_performance = update_chart_layout(sales_rep_performance)
        
        age_distribution = px.histogram(dff, x='age', nbins=20, title="Customer Age Distribution",
                                        color_discrete_sequence=[colors['primary']], labels={'age':'Age', 'count':'Number of Customers'})
        age_distribution.update_traces(hovertemplate='Age: %{x}<br>Number of Customers: %{y}')
        age_distribution = update_chart_layout(age_distribution)
        
        return kpi_indicators, time_series, customer_purchase, product_sales, sales_rep_performance, age_distribution

    return app

def main():
    df = load_data()
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()