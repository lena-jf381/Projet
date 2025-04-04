import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from xhtml2pdf import pisa
import base64
import io


def filter(filename:str,date_min:datetime, date_max:datetime = None):
    columns = ['date', 'valeur']
    # Lis le fichier
    df = pd.read_csv(f'data_{filename.lower()}.csv', header = None, names=columns, sep=';')

    #convertit au format date dd/MM/YYYY H:M
    df['date'] = df['date'].apply(pd.to_datetime, dayfirst=True)
    df.dropna(inplace=True)

    if date_max is None:
        filtered_data = df.loc[(df['date'].dt.date >= date_min )]
    else:        
        filtered_data = df.loc[(df['date'].dt.date >= date_min )
                     & (df['date'].dt.date < date_max)]

   # print(filtered_data)   
    return filtered_data



#Quelques tests
#auj = datetime.now().date()
#demain = datetime.now().date()+ timedelta(days=3)

# On récupère les données du jour uniquement
#filtered_data = df.loc[(df['date'].dt.date >= auj)]

# On récupères les donénes dans une plage
# df = filter('data_google.csv',auj,demain)

def figure_to_base64(figures)->str:
    images_html = ""
    for figure in figures:
        image = str(base64.b64encode(figure.to_image(format="png", scale=2)))[2:-1]
        images_html += (f'<img src="data:image/png;base64,{image}"/>\n \
                        <br/>')
    return images_html
 
def create_html_report(template_file, images_html,date_generation)->str:
    with open(template_file,'r') as f:
        template_html = f.read()
    report_html = template_html.replace("{{ FIGURES }}", images_html) \
                    .replace("{{ DATE_GENERATION }}", date_generation)
    return report_html
 
def convert_html_to_pdf(source_html, output_filename):
    with open(f"{output_filename}", "w+b") as f:
        pisa_status = pisa.CreatePDF(source_html, dest=f)   
        return pisa_status.err


def make_img(actions, date_min, date_max:None ):
    #mode = 'lines+markers+text'
    mode = 'lines+text'
    fig = px.scatter(height=1000)
    
    for action in actions:
        df = filter(action,date_min.date(),date_max.date() if date_max is not None else None)
        fig.add_scatter(name=action.capitalize(), x=df['date'], y=df['valeur'], mode=mode)
    return fig


#start_date = datetime.now().date()
start_date = datetime(2025,3,26)
end_date = start_date+ timedelta(days=10)

actions= ['Apple','Amazon','Google','Meta','Microsoft','Nvidia']
fig=make_img(actions=actions, date_min=start_date, date_max=end_date)
                        

figures =[fig]
images_html = figure_to_base64(figures)

date_generation= start_date.strftime("%d/%m/%Y")

report_html = create_html_report("template.html", images_html, date_generation)

with open(f"reports/report{start_date.strftime("%Y-%m-%d")}.html", "w") as f:
    f.write(report_html)

convert_html_to_pdf(report_html, f"reports/report{start_date.strftime("%Y-%m-%d")}.pdf")
