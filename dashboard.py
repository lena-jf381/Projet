import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime, timedelta, date
from flask import Flask,send_from_directory
import os
#from collections import namedtuple

# On crée ue classe pour stocker les informations de chaque graphique
class InfoChart:
    def __init__(self, name, data, figure, figure_color, min, max, mean, std, median):
        self.name = name
        self.data = data
        self.figure = figure
        self.figure_color = figure_color
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std
        self.median = median
        self.text_info = f"Valeurs {name} : min={self.min}, max={self.max}, moyenne={self.mean:.2f}, écart-type={self.std:.2f}, mediane={self.median:.2f}"
     
    
# On crée un namedtuple pour stocker les informations de chaque graphique
#InfoChart= namedtuple('InfoChart', ['figure', 'min', 'max', 'mean', 'std', 'median'])
                     
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

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.DARKLY])


# On crée un générateur de couleur pour les graphiques
def get_color():
    '''Renvoie une couleur différente dans un ordre cyclique'''
    while True:
        for c in ('#e74c3c','blue','green','orange','#2e40F3','#cb1dd1'):
            yield c
color_generator = get_color()

# On crée une fonction pour obtenir les informations sur une action
def get_info_stock(nom, start_date, end_date)->InfoChart:
    """
    Obtient des informations pour une action donnée

    :param nom: nom de l'action (ex: "Apple")
    :param start_date: date de début du graphique (datetime.date)
    :param end_date: date de fin du graphique (datetime.date)
    :return: les inforamtions sur une action (InfoChart)
    """
    fig = px.scatter(template=template)
    columns = ['date', 'valeur']
    mode = 'lines+markers+text'

    # Charge le fichier, met en index la date (colonne 0) avec le format Jour/Mois/Année Heure:Minute
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

    color = next(color_generator)
    #Formate la colonne en date
    fig.add_scatter(name=nom.capitalize(), x=data.index, y=data['valeur'], mode=mode, line_color= color)
    #fig.update_layout(xaxis=dict(tickformat="%d/%m/%y"))
 
    # On renvoie les infos
    rst= InfoChart(name=nom,data=data,figure=fig, figure_color=color,
                   min=data['valeur'].min(), max=data['valeur'].max(), mean=data['valeur'].mean(), std=data['valeur'].std(), median=data['valeur'].median())                
    #return fig, data['valeur'].min(), data['valeur'].max(), data['valeur'].mean(), data['valeur'].std(), data['valeur'].median()
    return rst


# On a commencé le tracing à partir du 28 mars 2025
min_date_allowed = datetime(2025,3,28)

# On affiche nos graphiques par défaut sur une semaine glissante
init_date =  datetime.now() - timedelta(days=2)


row_menu = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button("Rapports PDF quotidiens", id="rapports_button", href="/"), width=2, class_name="m-1"),
        dbc.Col(dbc.Button("Téléchargement Données",id="data_button", n_clicks=0), width=2, class_name="m-1"),
        dbc.Col(dbc.Button("Informations sur le site",id="info_button", n_clicks=0), width=2, class_name="m-1"),
        dbc.Col(dbc.Button("Lien Github", href="https://github.com/lena-jf381/Projet", target="_blank"), width=2, class_name="m-1"),
      
    ],justify="end"), 

    # Fenêtre modale pour les rapports quotidients
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("PDF quotidients")),
                dbc.ModalBody([
                        html.Label("Ce site génère à 20h00 des rapports quotidiens au format PDF contenant les graphiques des actions technologiques. "),
                        html.Ul(id="rapports_list", className="m-2"), # Liste des rapports
                    ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="rapports_btn_close", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal_rapports",
            scrollable=True, #On rend la fenêtre modale scrollable
            is_open=False,
        ), 

    # Fenêtre modale pour les informations
     dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Informations")),
                dbc.ModalBody(
                          html.Label("Le site sur lequel nous récupérons des données (wise.com) rencontre périodiquement des problèmes de caching au sens où il renvoie d'anciennes valeurs "
     "ou des problèmes de données au sens où il n'affiche pas la valeur. Ce comportement arrive généralement lors des phases de clotures de marché ou de nuit."
     "Pour ces raisons, il y a parfois des données manquantes dans le dashboard, ou qu'il y a alternance, sur de très courtes périodes, entre des anciens et nouveaux prix",
        style={'color': 'yellow', 'font-size': '14px'}, className="m-2")),
                dbc.ModalFooter(
                    dbc.Button("Close", id="info_btn_close", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal_info",
            is_open=False,
        ), 

    
    #Fenêtre modale pour le téléchargement des données
     dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Fichiers de données")),
                dbc.ModalBody([
                          html.Label("Ce site se met à jour tout seul grâce à un scraper. Vous pouvez télécharger les données utilisées grâce aux liens ci-dessous.",
                                    style={'font-size': '14px'}, className="m-2"),
                          html.Label("Attention, certaines données sont vides car le site où l'on scrappe les données rencontre certains problèmes notamment dans la nuit.", style={'font-size': '14px', 'color':'red'},
                                      className="m-2"),
                          html.Ul([
                                html.Li(html.A("data_apple.csv", href="/data/data_apple.csv", target="_blank")),
                                html.Li(html.A("data_amazon.csv", href="/data/data_amazon.csv", target="_blank")),
                                html.Li(html.A("data_google.csv", href="/data/data_google.csv", target="_blank")),
                                html.Li(html.A("data_meta.csv", href="/data/data_meta.csv", target="_blank")),
                                html.Li(html.A("data_microsoft.csv", href="/data/data_microsoft.csv", target="_blank")),
                                html.Li(html.A("data_nvidia.csv", href="/data/data_nvidia.csv", target="_blank")),
                            ], className="m-2"),
                            ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="data_btn_close", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal_download",
            is_open=False,
        ), 

    # Fenêtre modale qui se lance au démarrage de l'application avec des URLs de téléchargement si un développeur veut tester l'application mais qu'il n'a pas lancé le scrapper 
     dbc.Modal(
            [ 
                dbc.ModalHeader(dbc.ModalTitle("ATTENTION PAS DE DONNEES",style={'color': 'red'})),
                dbc.ModalBody([
                            html.Label("Ce site se met à jour tout seul grâce à un scraper. Vous tentez de lancer l'application en local avant que le scraper ait été lancé. "
                                "Si vous ne pouvez pas lancer le scrapper, merci de télécharger les fichiers ci-dessous qui sont en provenance de la VM "
                                " https://vmlinuxlena.eastus.cloudapp.azure.com.",
                                
                               style={'font-size': '14px'}, className="m-2")
                            ,html.Ul([
                                html.Li(html.A("data_apple.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_apple.csv", target="_blank")),
                                html.Li(html.A("data_amazon.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_amazon.csv", target="_blank")),
                                html.Li(html.A("data_google.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_google.csv", target="_blank")),
                                html.Li(html.A("data_meta.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_meta.csv", target="_blank")),
                                html.Li(html.A("data_microsoft.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_microsoft.csv", target="_blank")),
                                html.Li(html.A("data_nvidia.csv", href="https://vmlinuxlena.eastus.cloudapp.azure.com/data/data_nvidia.csv", target="_blank")),
                            ], className="m-2"),
                            html.Label("Merci de mettre ces fichiers dans le même répertoire que le dashboard.py pour que l'application fonctionne.",
                                       style={'font-size': '14px','color':'red'}, className="m-2"),
                            ]),
            ],
            id="modal_data_file_missing",
            is_open=False,
        ), 
])

# Permet l'ouverture/fermeture de la fenêtre modale pour les rapports
@app.callback(
    Output("modal_rapports", "is_open"),    
    [Input("rapports_button", "n_clicks"), Input("rapports_btn_close", "n_clicks")],
    [State("modal_rapports", "is_open")],
)
def toggle_modal_rapports(n1, n2, is_open):
    if n1 or n2:
        return not is_open        
    return is_open


# Permet l'ouverture/fermeturede la fenêtre modale pour les infos
@app.callback(
    Output("modal_info", "is_open"),    
    [Input("info_button", "n_clicks"), Input("info_btn_close", "n_clicks")],
    [State("modal_info", "is_open")],
)
def toggle_modal_info(n1, n2, is_open):
    if n1 or n2:
        return not is_open        
    return is_open



# Permet l'ouverture/fermeture la fenêtre modale pour le téléchargement des données
@app.callback(
    Output("modal_download", "is_open"),    
    [Input("data_button", "n_clicks"), Input("data_btn_close", "n_clicks")],
    [State("modal_download", "is_open")],
)
def toggle_modal_download(n1, n2, is_open):
    if n1 or n2:
        return not is_open        
    return is_open

  
# Permet le téléchargement des rapports
@server.route("/reports/<path:path>")
def download(path):
    return send_from_directory('reports', path, as_attachment=False)

# Permet le téléchargement des données
@server.route("/data/<path:path>")
def download_data(path):
    if path.endswith('.csv'):  # On se protège en ne téléchargeant que les fichiers csv
        return send_from_directory('', path, as_attachment=True)
    

# Permet l'affichage de la liste des rapports
@app.callback(
    Output("rapports_list", "children"),    
    [Input("rapports_button", "n_clicks")],    
    prevent_initial_call=True,  # On ne l'affiche pas au démarrage
)
def get_list_rapports(n_click):
    # On ne prend que les pdfs  (en clair, ce que l'on a généré)
    files =  list(filter(lambda file: file.endswith('.pdf') ,os.listdir('reports')))
    
    # On trie les fichiers par ordre décroissant (le plus récent d'abord)
    # Comme on nomme les fichiers avec la date au format YYYY-MM-DD, on peut 
    # le faire facilement
    files.sort(reverse=True) 

    

    content=[]

    for rapport in files:
        # On formate les noms auu format DD/MM/YYYY et on renvoie les liens
        annee=rapport[7:11]
        mois=rapport[12:14]
        jour=rapport[15:17]
        nom_visuel='Rapport du ' + jour + '/' + mois + '/' + annee
        content.append(
                dash.html.Li(
                    dash.html.A(nom_visuel, href=f"/reports/{rapport}", target="_blank"), className="m-2"
                         )
         )
    return content


# Permet l'affichage de la fenêtre modale "data_file_missings"
@app.callback(
    Output("modal_data_file_missing", "is_open"),    
    Input('info_button','style'),  # Grosse astuce. Le style n'est jamais appelé dans notre code. Cet appel a lieu une fois au démarrage de l'application
    [State("modal_data_file_missing", "is_open")],
)
def toggle_modal_data_file_missing(style, is_open):
    return not os.path.isfile('data_apple.csv')     # Si data_apple.csv
    

# On initialise le Dashborard
app.layout = html.Div([
    html.H1("Actions technologiques"),

    # On affiche le menu avec les boutons
    row_menu,

    html.Hr(),
    
    html.Div([
        html.Label("Sélectionner une plage de dates :",
            style={'font-weight': 'bold', 'font-size': '20px'}),    
    

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
            className="m-4")
    ]),
    
    
    html.H4("Apple", className="m-4"),
    dcc.Graph(id='graph-apple', className="m-4"),    
    html.Label(id='lbl-info-apple',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    html.H4("Amazon", className="m-4"),    
    dcc.Graph(id='graph-amazon', className="m-4"),
    html.Label(id='lbl-info-amazon',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    html.H4("Google", className="m-4"),
    dcc.Graph(id='graph-google', className="m-4"),
    html.Label(id='lbl-info-google',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    html.H4("Meta", className="m-4"),
    dcc.Graph(id='graph-meta', className="m-4"),
    html.Label(id='lbl-info-meta',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    html.H4("Microsoft", className="m-4"),
    dcc.Graph(id='graph-microsoft', className="m-4"),
    html.Label(id='lbl-info-microsoft',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    html.H4("Nvidia", className="m-4"),
    dcc.Graph(id='graph-nvidia', className="m-4"),    
    html.Label(id='lbl-info-nvidia',style={'color': next(color_generator)}, className="d-flex justify-content-center"),

    # Intervalle de mise à jour toutes les 60 secondes
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 secondes en millisecondes
        n_intervals=0
    ),

])



@app.callback(
    [Output('graph-apple','figure'), Output('lbl-info-apple','children'),
     Output('graph-amazon','figure'),  Output('lbl-info-amazon','children'),
     Output('graph-google','figure'),  Output('lbl-info-google','children'),
     Output('graph-meta','figure'),  Output('lbl-info-meta','children'),
     Output('graph-microsoft','figure'),  Output('lbl-info-microsoft','children'),
     Output('graph-nvidia','figure'), Output('lbl-info-nvidia','children')     
    ],
    [Input('interval-component', 'n_intervals'),
     Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_dashboard(n_intervals, start_date, end_date):        
    
    #Figure = px.scatter()

    deb_date=  date.fromisoformat(start_date) if start_date is not None else init_date.date()
    fin_date=  date.fromisoformat(end_date) if end_date is not None else datetime.now().date()
        
    #On ajoute des valeurs technologiques
    apple=get_info_stock("Apple",deb_date,fin_date)
    amazon=get_info_stock("Amazon",deb_date,fin_date)
    google=get_info_stock("Google",deb_date,fin_date)
    meta=get_info_stock("Meta",deb_date,fin_date)
    microsoft=get_info_stock("Microsoft",deb_date,fin_date)
    nvidia =get_info_stock("Nvidia",deb_date,fin_date)
    

    return  apple.figure, apple.text_info, \
            amazon.figure,amazon.text_info, \
            google.figure, google.text_info, \
            meta.figure,meta.text_info, \
            microsoft.figure,microsoft.text_info,\
            nvidia.figure, nvidia.text_info          


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    server = app.server

