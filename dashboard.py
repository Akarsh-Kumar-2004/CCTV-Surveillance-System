import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import glob

app = dash.Dash(__name__)

# data = pd.DataFrame({
#     "Time": ["2025-04-25 12:00", "2025-04-25 12:10", "2025-04-25 12:20"],
#     "People Count": [10, 15, 20],
# })


def load_data():
    files = glob.glob("logs/traffic_log_*.csv")
    if not files:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(f) for f in files])
    return df

app.layout = html.Div(style={
    'backgroundColor': '#0f172a',
    'color': '#e2e8f0',
    'fontFamily': 'Arial, sans-serif',
    'padding': '20px'
}, children=[
    html.H1(children="Surveillance Dashboard", style={'textAlign': 'center', 'color': '#38bdf8'}),
    html.Div(children="In/Out people count, posture distribution, and alert trends (live update every 10 sec).", style={'textAlign': 'center', 'marginBottom': '20px'}),
    dcc.Graph(id="people-count-graph"),
    dcc.Graph(id="posture-graph"),
    dcc.Graph(id="alert-graph"),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    ),
])

@app.callback(
    [dash.dependencies.Output("people-count-graph", "figure"),
     dash.dependencies.Output("posture-graph", "figure"),
     dash.dependencies.Output("alert-graph", "figure")],
    [dash.dependencies.Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    df = load_data()

    if df.empty:
        empty_fig = px.line(title="No Data Yet")
        empty_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return empty_fig, empty_fig, empty_fig

    # Normalize time column
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df = df.dropna(subset=['time']).sort_values('time')

    # People flow chart with IN and OUT
    people_fig = px.line(df, x='time', y=['in', 'out'],
                         title='People Flow (IN/OUT)',
                         labels={'value': 'Count', 'time': 'Timestamp'},
                         color_discrete_sequence=['#22c55e', '#ef4444'])
    people_fig.update_traces(mode='lines+markers')
    people_fig.update_layout(
        paper_bgcolor='#0f172a',
        plot_bgcolor='#0e1a2a',
        font_color='#e2e8f0',
        legend_title_text='Direction'
    )

    # Posture distribution
    if 'posture' in df.columns and not df['posture'].isna().all():
        posture_counts = df['posture'].fillna('Unknown').value_counts().reset_index()
        posture_counts.columns = ['posture', 'count']
        posture_fig = px.bar(posture_counts, x='posture', y='count',
                             title='Posture Distribution',
                             labels={'count': 'Frames', 'posture': 'Posture State'},
                             color='posture',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
        posture_fig.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0e1a2a', font_color='#e2e8f0')
    else:
        posture_fig = px.bar(title='Posture Distribution (no data yet)')
        posture_fig.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0e1a2a', font_color='#e2e8f0')

    # Alert trend chart
    if 'alert' in df.columns and not df['alert'].fillna('').eq('').all():
        alerts = df[['time', 'alert']].copy()
        alerts['alert_type'] = alerts['alert'].fillna('').str.split('\s+')
        alerts = alerts.explode('alert_type')
        alerts = alerts[alerts['alert_type'] != '']
        if not alerts.empty:
            alert_counts = alerts.groupby(['time', 'alert_type']).size().reset_index(name='count')
            alert_fig = px.area(alert_counts, x='time', y='count', color='alert_type',
                                title='Alert Type Trends',
                                labels={'count': 'Occurrences', 'alert_type': 'Alert Type'})
            alert_fig.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0e1a2a', font_color='#e2e8f0')
        else:
            alert_fig = px.area(title='Alert Type Trends (no alerts yet)')
            alert_fig.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0e1a2a', font_color='#e2e8f0')
    else:
        alert_fig = px.area(title='Alert Type Trends (no data yet)')
        alert_fig.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0e1a2a', font_color='#e2e8f0')

    return people_fig, posture_fig, alert_fig

if __name__ == '__main__':
    app.run(debug=True)
