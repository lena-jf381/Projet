import dash
from dash import dcc, html

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Définition du layout du dashboard
app.layout = html.Div(children=[
    html.H1(children='Mon Dashboard Dash'),

    html.Div(children='''
        Voici un exemple de dashboard avec Dash.
    '''),

    dcc.Graph(
        id='exemple-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Exemple'},
            ],
            'layout': {
                'title': 'Graphique d\'exemple'
            }
        }
    )
])

if __name__ == '__main__':
    app.run(debug=True)