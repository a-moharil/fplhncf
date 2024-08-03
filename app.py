import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go

# Update categories for visualization
column_categories = {
    'Performance Metrics': ['total_points', 'goals_scored', 'assists', 'clean_sheets'],
    'Minutes Played': ['minutes'],  # New category for minutes played
    'Cost and Value Metrics': ['now_cost', 'value_form', 'value_season'],
    'Rankings and Indices': ['ict_index', 'form', 'threat', 'influence', 'creativity'],
    'Event Specific Data': ['transfers_in_event', 'transfers_out_event', 'event_points'],
    'Penalties and Cards': ['penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards']
}

def load_data(file_path):
    return pd.read_csv(file_path)

app = dash.Dash(__name__)
df = load_data('players.csv')

app.layout = html.Div([
    dcc.Input(id='player1-input', type='text', placeholder='Enter first player name...'),
    dcc.Input(id='player2-input', type='text', placeholder='Enter second player name (optional)...', style={'margin-top': '10px'}),
    html.Button('Submit Player 1', id='submit-button1', n_clicks=0),
    html.Button('Submit Player 2', id='submit-button2', n_clicks=0),
    dcc.Dropdown(id='player1-select', options=[], style={'width': '50%'}, placeholder='Select first player'),
    dcc.Dropdown(id='player2-select', options=[], style={'width': '50%'}, placeholder='Select second player'),
    dcc.Input(id='team1-input', type='text', placeholder='Enter first team name...', style={'margin-top': '20px'}),
    dcc.Input(id='team2-input', type='text', placeholder='Enter second team name (optional)...', style={'margin-top': '10px'}),
    html.Button('Submit Team 1', id='submit-button3', n_clicks=0),
    html.Button('Submit Team 2', id='submit-button4', n_clicks=0),
    dcc.Dropdown(id='team1-select', options=[], style={'width': '50%'}, placeholder='Select first team'),
    dcc.Dropdown(id='team2-select', options=[], style={'width': '50%'}, placeholder='Select second team'),
    dcc.Dropdown(
        id='chart-type-select',
        options=[
            {'label': 'Radar Chart', 'value': 'radar'},
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Scatter Chart', 'value': 'scatter'},
            {'label': 'Area Chart', 'value': 'area'},
            {'label': 'Box Plot', 'value': 'box'}
        ],
        value='radar',
        style={'width': '50%'},
        placeholder='Select chart type'
    ),
    html.Button('Generate Analysis', id='generate-analysis', n_clicks=0),
    html.Div(id='graphs-container')
])

@app.callback(
    [Output('player1-select', 'options'), Output('player2-select', 'options')],
    [Input('submit-button1', 'n_clicks'), Input('submit-button2', 'n_clicks')],
    [State('player1-input', 'value'), State('player2-input', 'value')]
)
def update_player_options(n_clicks1, n_clicks2, player1_name, player2_name):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'submit-button1' and player1_name:
        player1_options = [{'label': player['name'], 'value': idx} for idx, player in df[df['name'].str.contains(player1_name, case=False, na=False)].iterrows()]
        return player1_options, dash.no_update
    elif button_id == 'submit-button2' and player2_name:
        player2_options = [{'label': player['name'], 'value': idx} for idx, player in df[df['name'].str.contains(player2_name, case=False, na=False)].iterrows()]
        return dash.no_update, player2_options
    return [], []

@app.callback(
    [Output('team1-select', 'options'), Output('team2-select', 'options')],
    [Input('submit-button3', 'n_clicks'), Input('submit-button4', 'n_clicks')],
    [State('team1-input', 'value'), State('team2-input', 'value')]
)
def update_team_options(n_clicks1, n_clicks2, team1_name, team2_name):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'submit-button3' and team1_name:
        team1_options = [{'label': team, 'value': team} for team in df['team'].unique() if team1_name.lower() in team.lower()]
        return team1_options, dash.no_update
    elif button_id == 'submit-button4' and team2_name:
        team2_options = [{'label': team, 'value': team} for team in df['team'].unique() if team2_name.lower() in team.lower()]
        return dash.no_update, team2_options
    return [], []

@app.callback(
    Output('graphs-container', 'children'),
    [Input('generate-analysis', 'n_clicks')],
    [State('player1-select', 'value'), State('player2-select', 'value'), State('team1-select', 'value'), State('team2-select', 'value'), State('chart-type-select', 'value')]
)
def generate_visualizations(n_clicks, player1_id, player2_id, team1_name, team2_name, chart_type):
    if n_clicks == 0:
        return []
    players = [df.iloc[idx] for idx in [player1_id, player2_id] if idx is not None]
    teams = [df[df['team'] == team_name] for team_name in [team1_name, team2_name] if team_name]
    team_colors = ['blue', 'green']  # Assign colors for the two teams

    graphs = []
    for category, metrics in column_categories.items():
        fig = go.Figure()
        for player_data in players:
            if chart_type == 'radar':
                normalized_values = [(player_data[metric] - df[metric].min()) / (df[metric].max() - df[metric].min()) for metric in metrics]
                fig.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=metrics,
                    fill='toself',
                    name=player_data['name']
                ))
            elif chart_type == 'bar':
                fig.add_trace(go.Bar(
                    x=metrics,
                    y=[player_data[metric] for metric in metrics],
                    name=player_data['name']
                ))
            elif chart_type == 'line':
                fig.add_trace(go.Scatter(
                    x=metrics,
                    y=[player_data[metric] for metric in metrics],
                    mode='lines+markers',
                    name=player_data['name']
                ))
            elif chart_type == 'scatter':
                fig.add_trace(go.Scatter(
                    x=metrics,
                    y=[player_data[metric] for metric in metrics],
                    mode='markers',
                    name=player_data['name']
                ))
            elif chart_type == 'area':
                fig.add_trace(go.Scatter(
                    x=metrics,
                    y=[player_data[metric] for metric in metrics],
                    fill='tozeroy',
                    name=player_data['name']
                ))

        for team_data, color in zip(teams, team_colors):
            if chart_type == 'box':
                for metric in metrics:
                    min_val = df[metric].min()
                    max_val = df[metric].max()
                    normalized_metric = (team_data[metric] - min_val) / (max_val - min_val)
                    fig.add_trace(go.Box(
                        y=normalized_metric,
                        name=f"{team_data['team'].iloc[0]} - {metric}",
                        boxpoints='all',  # Display original data points
                        jitter=0.5,  # Spread points to avoid overlap
                        pointpos=-1.8,  # Position points relative to the box
                        marker=dict(color=color, size=5),
                        line=dict(color=color),
                        text=team_data['name'],  # Player names as labels
                        hoverinfo='text+y'
                    ))
                fig.update_layout(title=f"Normalized Box Plot of {category}", boxmode='group')
            else:
                aggregated_data = team_data[metrics].mean()  # Mean values for other visualizations
                if chart_type == 'radar':
                    normalized_values = [(aggregated_data[metric] - df[metric].min()) / (df[metric].max() - df[metric].min()) for metric in metrics]
                    fig.add_trace(go.Scatterpolar(
                        r=normalized_values,
                        theta=metrics,
                        fill='toself',
                        name=team_data['team'].iloc[0],
                        line=dict(color=color)
                    ))
                elif chart_type == 'bar':
                    fig.add_trace(go.Bar(
                        x=metrics,
                        y=aggregated_data,
                        name=team_data['team'].iloc[0],
                        marker=dict(color=color)
                    ))
                elif chart_type == 'line':
                    fig.add_trace(go.Scatter(
                        x=metrics,
                        y=aggregated_data,
                        mode='lines+markers',
                        name=team_data['team'].iloc[0],
                        line=dict(color=color)
                    ))
                elif chart_type == 'scatter':
                    fig.add_trace(go.Scatter(
                        x=metrics,
                        y=aggregated_data,
                        mode='markers',
                        name=team_data['team'].iloc[0],
                        marker=dict(color=color, size=10)
                    ))
                elif chart_type == 'area':
                    fig.add_trace(go.Scatter(
                        x=metrics,
                        y=aggregated_data,
                        fill='tozeroy',
                        name=team_data['team'].iloc[0],
                        line=dict(color=color)
                    ))

        fig.update_layout(margin=dict(l=20, r=20, t=40))
        graphs.append(html.Div(dcc.Graph(figure=fig), style={'flex': '1 1 50%'}))

    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)
