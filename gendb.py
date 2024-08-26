import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

load_dotenv()

def create_app(df):
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['completed_date'] = pd.to_datetime(df['completed_date'])
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
        'padding': '15px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
        'margin': '10px',
        'width': '220px',
        'height': '150px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between',
        'transition': 'all 0.3s ease'
    }

    category_options = [{'label': 'Select All', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df.category.unique()]
    priority_options = [{'label': 'Select All', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df.priority.unique()]
    status_options = [{'label': 'Select All', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df.status.unique()]

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
            html.H1('Task Management Dashboard', style={
                'textAlign': 'center',
                'color': colors['text'],
                'marginBottom': '30px',
                'fontSize': '36px',
                'fontWeight': '300',
                'letterSpacing': '2px'
            }),
            
            html.Div([
                html.Div([
                    html.Label('Category', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-category',
                        options=category_options,
                        value=['ALL'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Priority', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-priority',
                        options=priority_options,
                        value=['ALL'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Status', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-status',
                        options=status_options,
                        value=['ALL'],
                        multi=True,
                        style={'width': '300px'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column'}),
                html.Div([
                    html.Label('Date Range', style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=df['due_date'].min(),
                        end_date=df['due_date'].max(),
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
                dbc.Col([dcc.Graph(id='task-status')], width=6),
                dbc.Col([dcc.Graph(id='priority-distribution')], width=6),
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='category-breakdown')], width=6),
                dbc.Col([dcc.Graph(id='time-estimation-accuracy')], width=6),
            ], className='mb-4'),
            
        ], style={
            'fontFamily': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
            'padding': '20px',
            'backgroundColor': colors['background']
        })
    ], fluid=True)

    @callback(
        [Output('kpi-indicators', 'children'),
         Output('task-status', 'figure'),
         Output('priority-distribution', 'figure'),
         Output('category-breakdown', 'figure'),
         Output('time-estimation-accuracy', 'figure'),
         Output('dropdown-category', 'value'),
         Output('dropdown-priority', 'value'),
         Output('dropdown-status', 'value'),
         Output('date-picker-range', 'start_date'),
         Output('date-picker-range', 'end_date')],
        [Input('dropdown-category', 'value'),
         Input('dropdown-priority', 'value'),
         Input('dropdown-status', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('task-status', 'clickData'),
         Input('priority-distribution', 'clickData'),
         Input('category-breakdown', 'clickData'),
         Input('time-estimation-accuracy', 'selectedData'),
         Input('reset-button', 'n_clicks')],
        [State('dropdown-category', 'options'),
         State('dropdown-priority', 'options'),
         State('dropdown-status', 'options')]
    )
    def update_dashboard(categories, priorities, statuses, start_date, end_date, task_status_click, priority_click, category_click, time_accuracy_selection, reset_clicks, category_options, priority_options, status_options):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        dff = df.copy()
        if 'ALL' not in categories:
            dff = dff[dff.category.isin(categories)]
        if 'ALL' not in priorities:
            dff = dff[dff.priority.isin(priorities)]
        if 'ALL' not in statuses:
            dff = dff[dff.status.isin(statuses)]
        dff = dff[(dff.due_date >= start_date) & (dff.due_date <= end_date)]
        
        if ctx.triggered:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if input_id == 'reset-button':
                categories = ['ALL']
                priorities = ['ALL']
                statuses = ['ALL']
                start_date = df['due_date'].min()
                end_date = df['due_date'].max()
                dff = df[(df.due_date >= start_date) & (df.due_date <= end_date)]
            elif input_id == 'task-status' and task_status_click:
                status = task_status_click['points'][0]['label']
                statuses = [status]
                dff = dff[dff['status'] == status]
            elif input_id == 'priority-distribution' and priority_click:
                priority = priority_click['points'][0]['x']
                priorities = [priority]
                dff = dff[dff['priority'] == priority]
            elif input_id == 'category-breakdown' and category_click:
                category = category_click['points'][0]['x']
                categories = [category]
                dff = dff[dff['category'] == category]
            elif input_id == 'time-estimation-accuracy' and time_accuracy_selection:
                time_range = [time_accuracy_selection['range']['x'][0], time_accuracy_selection['range']['x'][1]]
                dff = dff[(dff['estimated_time'] >= time_range[0]) & (dff['estimated_time'] <= time_range[1])]

        total_tasks = len(dff)
        completed_tasks = len(dff[dff['status'] == 'Completed'])
        overdue_tasks = len(dff[(dff['status'] != 'Completed') & (dff['due_date'] < pd.Timestamp.now())])
        avg_completion_time = (dff['completed_date'] - dff['due_date']).mean().days if 'completed_date' in dff.columns else 0
        
        past_start_date = start_date - timedelta(days=180)
        past_end_date = end_date - timedelta(days=180)
        past_dff = df[(df.due_date >= past_start_date) & (df.due_date <= past_end_date)]
        
        past_total_tasks = len(past_dff)
        past_completed_tasks = len(past_dff[past_dff['status'] == 'Completed'])
        past_overdue_tasks = len(past_dff[(past_dff['status'] != 'Completed') & (past_dff['due_date'] < pd.Timestamp.now())])
        past_avg_completion_time = (past_dff['completed_date'] - past_dff['due_date']).mean().days if 'completed_date' in past_dff.columns else 0
        
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
        
        kpi_indicators = html.Div([
            create_kpi_card('Total Tasks', total_tasks, past_total_tasks),
            create_kpi_card('Completed Tasks', completed_tasks, past_completed_tasks),
            create_kpi_card('Overdue Tasks', overdue_tasks, past_overdue_tasks),
            create_kpi_card('Avg Completion Time (days)', avg_completion_time, past_avg_completion_time)
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'stretch', 'flexWrap': 'wrap'})
        
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
        
        task_status = px.pie(dff, names='status', title="Task Status Distribution",
                             color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent'], colors['negative']])
        task_status = update_chart_layout(task_status)
        
        priority_distribution = px.bar(dff, x='priority', y='task_name', title="Task Priority Distribution",
                                       color='priority', color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent'], colors['negative']])
        priority_distribution = update_chart_layout(priority_distribution)
        
        category_breakdown = px.bar(dff, x='category', y='task_name', title="Task Category Breakdown",
                                    color='category', color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent'], colors['negative']])
        category_breakdown = update_chart_layout(category_breakdown)
        
        time_estimation_accuracy = px.scatter(dff, x='estimated_time', y='actual_time', title="Time Estimation Accuracy",
                                              color='category', hover_data=['task_name'], color_discrete_sequence=[colors['primary'], colors['secondary'], colors['accent'], colors['negative']])
        time_estimation_accuracy.add_shape(type="line", x0=0, y0=0, x1=dff['estimated_time'].max(), y1=dff['estimated_time'].max(),
                                           line=dict(color="red", width=2, dash="dash"))
        time_estimation_accuracy = update_chart_layout(time_estimation_accuracy)
        
        return kpi_indicators, task_status, priority_distribution, category_breakdown, time_estimation_accuracy, categories, priorities, statuses, start_date, end_date

    return app

def main():
    df_path = "C:/Users/aditya/Desktop/2024/auto-dash/Staging_Data/engineered_data.csv"
    df = pd.read_csv(df_path)
    app = create_app(df)
    app.run(debug=True)

if __name__ == '__main__':
    main()