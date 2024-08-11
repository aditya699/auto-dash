from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df=pd.read_csv("Raw_Sales/sales_data_1.csv")

app = Dash()

app.layout = [
    html.H1(children='Sales App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Portugal', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.bar(dff, x='customer_name', y='purchase_amount')


if __name__ == '__main__':
    app.run(debug=True)