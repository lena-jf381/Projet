import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Cours des actions technologiques"),

    dcc.Graph(id='cases-graph'),
    # Intervalle de mise à jour toutes les 60 secondes
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # 5 min * 60 secondes en millisecondes
        n_intervals=0
    )
])

def make_line(fig,nom):
    columns = ['date', 'valeur']
    mode = 'lines+markers+text'
    data = pd.read_csv(f'data_{nom.lower()}.csv', header = None, names=columns, sep=';')  
    #Formate la colonne en date
    data['date'] = data['date'].apply(pd.to_datetime, dayfirst=True)
    fig.add_scatter(name=nom.capitalize(), x=data['date'], y=data['valeur'], mode=mode)
 
@app.callback(
    [Output('cases-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):        
    
    figure = px.scatter()
    make_line(figure,"Google")
    #On ajoute des valeurs technologiques
    make_line(figure,"Apple")
    make_line(figure,"Amazon")
    
    make_line(figure,"Meta")
    make_line(figure,"Microsoft")
    make_line(figure,"Nvidia")    
    
    return [figure]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    server = app.server

