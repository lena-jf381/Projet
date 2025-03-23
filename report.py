import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from xhtml2pdf import pisa
import base64

def filter(file:str,date_min:datetime, date_max:datetime = None):
    columns = ['date', 'valeur']
    # Lis le fichier
    df = pd.read_csv(file, header = None, names=columns, sep=';') 

    #convertit au format date dd/MM/YYYY H:M
    df['date'] = df['date'].apply(pd.to_datetime, dayfirst=True)

    if date_max is None:
        filtered_data = df.loc[(df['date'].dt.date >= date_min )]
    else:        
        filtered_data = df.loc[(df['date'].dt.date >= date_min )
                     & (df['date'].dt.date < date_max)]
        
    return filtered_data



#Quelques tests
#auj = datetime.now().date()
#demain = datetime.now().date()+ timedelta(days=3)

# On récupère les données du jour uniquement
#filtered_data = df.loc[(df['date'].dt.date >= auj)]

# On récupères les donénes dans une plage
# df = filter('data_google.csv',auj,demain)

def figure_to_base64(figures):
    images_html = ""
    for figure in figures:
        image = str(base64.b64encode(figure.to_image(format="png", scale=2)))[2:-1]
        images_html += (f'<img src="data:image/png;base64,{image}"><br>')
    return images_html
 
def create_html_report(template_file, images_html):
    with open(template_file,'r') as f:
        template_html = f.read()
    report_html = template_html.replace("{{ FIGURES }}", images_html)
    return report_html
 
def convert_html_to_pdf(source_html, output_filename):
    with open(f"{output_filename}", "w+b") as f:
        pisa_status = pisa.CreatePDF(source_html, dest=f)
    return pisa_status.err

fig1 = px.scatter()
mode = 'lines+markers+text'

df = filter('data_google.csv',datetime.now().date())
fig1.add_scatter(name='Apple', x=df['date'], y=df['valeur'], mode=mode)


figures =[fig1]
#fig1.write_html('reports/example_fig.html') 
fig1.write_image('reports/exemple.png', engine="orca")
#images_html = figure_to_base64(figures)
 #report_html = create_html_report("template.html", images_html)
#convert_html_to_pdf(report_html, "/reports/report.pdf")
