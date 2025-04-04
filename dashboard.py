import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime, timedelta, date
templates = [
    "bootstrap",
    "minty",
    "pulse",
    "flatly",
    "quartz",
    "cyborg",
    "darkly",
    "vapor",
]

template='darkly'
load_figure_template(templates)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


def make_line(nom, start_date=None, end_date=None):
    fig = px.scatter(template=template)
    columns = ['date', 'valeur']
    mode = 'lines+markers+text'
#    data = pd.read_csv(f'data_{nom.lower()}.csv', header = None, names=columns, sep=';')   
    # Charge le fichier, met en index la date (colonne 0) avec le format Jour/Mois/Année Heure:Minute
    #data = pd.read_csv(f'data_{nom.lower()}.csv',header=None, names=columns,date_format={'date':'%d-%m-%Y %H:%M'},sep=';',index_col=0)
    data = pd.read_csv(f'data_{nom.lower()}.csv',header=None, names=columns,sep=';') #index_col=0)
    data['valeur'] = pd.to_numeric(data['valeur'],errors='coerce')
    data['date']=pd.to_datetime(data['date'],dayfirst=True)
    data.dropna(inplace=True)
 
    # Récupère la plage du jour
    
    #  start_date = datetime(2025,3,28,00,0,0)
    #tomorrow = start_date + timedelta(hours=23,minutes=59)
    data = data.loc[(data['date'].dt.date>=start_date)
                    & (data['date'].dt.date<=end_date)]
   
    data.set_index('date', inplace=True)

    print(data)
    #Formate la colonne en date
    fig.add_scatter(name=nom.capitalize(), x=data.index, y=data['valeur'], mode=mode, line_color=next(color_generator))
    #fig.update_layout(xaxis=dict(tickformat="%d/%m/%y"))

    return fig

# On crée un générateur de couleur pour les graphiques
def get_color():
    while True:
        for c in ('red','blue','green','orange','#2e4053','#cb1dd1'):
            yield c

color_generator = get_color()


# On a commencé le tracing à partir du 28 mars 2025
min_date_allowed = datetime(2025,3,28)

# On affiche nos graphiques par défaut sur une semaine glissante
init_date =  datetime.now() - timedelta(days=2)

app.layout = html.Div([
    html.H1("Actions technologiques"),
    html.Label("Pour information, le site sur lequel nous récupérons des données périodiquement des problèmes de caching au sens où il renvoie d'anciennes valeurs."
     "Ce comportement arrive généralement lors des phases de clotures de marché."
     "Il est donc possible que les graphiques ne correspondent pas sur quelques valeurs à la réalité marché .",
        style={'color': 'yellow', 'font-size': '14px'}, className="m-2"),
    html.Div([html.Label("Sélectionner une plage de dates :",
        style={'font-weight': 'bold', 'font-size': '30px'}),
    dcc.DatePickerRange(
        id='date-picker',        
        start_date=init_date.date(),
        min_date_allowed=min_date_allowed.date(),        
        end_date=datetime.now().date(),
        max_date_allowed=datetime.now().date(),
        display_format='DD/MM/YYYY',
        start_date_placeholder_text='Date de début',
        end_date_placeholder_text='Date de fin', 
        minimum_nights=0,
        className="m-4")]),
    html.H4("Apple", className="m-4"),
    dcc.Graph(id='graph-apple', className="m-4"),
    html.H4("Amazon", className="m-4"),
    dcc.Graph(id='graph-amazon', className="m-4"),
    html.H4("Google", className="m-4"),
    dcc.Graph(id='graph-google', className="m-4"),
    html.H4("Meta", className="m-4"),
    dcc.Graph(id='graph-meta', className="m-4"),
    html.H4("Microsoft", className="m-4"),
    dcc.Graph(id='graph-microsoft', className="m-4"),
    html.H4("Nvidia", className="m-4"),
    dcc.Graph(id='graph-nvidia', className="m-4"),    
    # Intervalle de mise à jour toutes les 60 secondes
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 secondes en millisecondes
        n_intervals=0
    )
])



@app.callback(
    [Output('graph-apple','figure'), Output('graph-amazon','figure'),Output('graph-google','figure'),
     Output('graph-meta','figure'),Output('graph-microsoft','figure'),Output('graph-nvidia','figure')],
    [Input('interval-component', 'n_intervals'),
     Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_dashboard(n_intervals, start_date, end_date):        
    
    #Figure = px.scatter()

    deb_date=  date.fromisoformat(start_date) if start_date is not None else init_date.date()
    fin_date=  date.fromisoformat(end_date) if end_date is not None else datetime.now().date()
    #On ajoute des valeurs technologiques
    apple=make_line("Apple",deb_date,fin_date)
    amazon=make_line("Amazon",deb_date,fin_date)
    google=make_line("Google",deb_date,fin_date)
    meta=make_line("Meta",deb_date,fin_date)
    microsoft=make_line("Microsoft",deb_date,fin_date)
    nvidia =make_line("Nvidia",deb_date,fin_date)
    
    return apple,amazon,google,meta,microsoft,nvidia

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    server = app.server

