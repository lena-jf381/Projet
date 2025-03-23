import dash
from dash import dcc, html, Input, Output
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

app = dash.Dash(__name__)

def get_total_cases():
    url = "https://www.worldometers.info/coronavirus/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Erreur lors de la récupération des données :", e)
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    cas_span = soup.find("span", style="color:#aaa")
    if cas_span:
        # On retire les virgules et convertit en entier
        try:
            return int(cas_span.text.strip().replace(',', ''))
        except ValueError:
            return None
    return None

app.layout = html.Div([
    html.H1("Dashboard Coronavirus"),
    html.Div(id='total-cases', style={'fontSize': 24, 'margin': '20px'}),
    dcc.Graph(id='cases-graph'),
    # Intervalle de mise à jour toutes les 60 secondes
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 secondes en millisecondes
        n_intervals=0
    )
])

@app.callback(
    [Output('total-cases', 'children'),
     Output('cases-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    total_cases = get_total_cases()
    if total_cases is None:
        text = "Données non disponibles"
        y_value = 0
    else:
        text = f"Nombre total de cas : {total_cases}"
        y_value = total_cases

    # Création d'un graphique en barre pour afficher le nombre de cas
    figure = go.Figure(
        data=[go.Bar(x=["Coronavirus"], y=[y_value], name="Cas")],
        layout=go.Layout(title="Nombre total de cas de Coronavirus")
    )
    return text, figure

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    server = app.server

