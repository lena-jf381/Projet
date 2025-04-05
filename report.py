import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from xhtml2pdf import pisa
import base64
import sys
from pypdf import PdfWriter
from pathlib import Path


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
 
def create_html_report(template_file, action, info_action,  images_html,date_generation, page_current, nb_pages)->str:
    with open(template_file,'r') as f:
        template_html = f.read()
    report_html = template_html.replace("{{ FIGURES }}", images_html) \
                    .replace("{{ ACTION }}", action) \
                    .replace("{{ DATE_GENERATION }}", date_generation) \
                    .replace("{{ PAGE_CURRENT }}", str(page_current)) \
                    .replace("{{ PAGE_COUNT }}", str(nb_pages)) \
                    .replace("{{ INFO }}", info_action)
    return report_html
 
def convert_html_to_pdf(source_html, output_filename):
    with open(f"{output_filename}", "w+b") as f:
        pisa_status = pisa.CreatePDF(source_html, dest=f)   
        return pisa_status.err


# Obtient les données sous la forme d'un dataframe et d'une figure
def get_info_and_make_img(action, date_min, date_max = None ):
    #mode = 'lines+markers+text'
    mode = 'lines+text'
    fig = px.scatter(height=700)
    
    
    df = filter(action,date_min.date(),date_max.date() if date_max is not None else None)
    fig.add_scatter(name=action.capitalize(), x=df['date'], y=df['valeur'], mode=mode)
    return df, fig



# On génère le PDF en faisant des "merges" de plusieurs PDF
# car la génération 'une PDF avec xhtml2pdf ne fonctionne pas bienavec plusieurs images
def generate_report(actions, start_date, end_date = None):
    Path("reports/tmp").mkdir(exist_ok=True)

    page =1 
    for action in actions:
        df, fig = get_info_and_make_img(action=action, date_min=start_date, date_max=end_date)

        col=df['valeur']   
        #print(col)                  
        info_action = f"Faits marquants {action} : min={col.min()}, max={col.max()}, moyenne={col.mean():.2f}, écart-type={col.std():.2f}, mediane={col.median():.2f}"

        figures =[fig]
        images_html = figure_to_base64(figures)

        date_generation= start_date.strftime("%d/%m/%Y")

        report_html = create_html_report(template_file= "template.html",
                                         action = action,
                                         images_html = images_html,
                                         info_action = info_action,
                                         date_generation= date_generation,
                                         page_current= page,
                                         nb_pages=len(actions))

        # On incrémente le numéro de page
        page +=1

        with open(f'reports/tmp/report-{action}.html', "w") as f:
            f.write(report_html)


        convert_html_to_pdf(report_html, f'reports/tmp/report-{action}.pdf')


    merger = PdfWriter()

    for action in actions:
        merger.append(f'reports/tmp/report-{action}.pdf')

    merger.write(f'reports/report-{start_date.strftime("%Y-%m-%d")}.pdf')
    merger.close()



def main():
    args = sys.argv[1:]
    #print('info:',args[0])
    
    start_date = datetime.now()

    if len(args)>0:
        try:
            print(args[0])
            #start_date = datetime.strptime(args[0], "%d/%m/%Y %H:%M")
            start_date = datetime.strptime(args[0], "%d/%m/%Y")
        except:
            print(f"Erreur de format de date {args[0]}. "
                  "Utilisation de la date du jour.")
            pass
    print('Generation du rapport pour la date:',start_date.date())
    #datetime.strptime('2014-12-04', '%Y-%m-%d').date()
    
    #start_date = datetime(2025,3,26)
    end_date = start_date + timedelta(days=1)

    actions= ['Apple','Amazon','Google','Meta','Microsoft','Nvidia']
    generate_report(actions, start_date, end_date=end_date)


if __name__ == "__main__":
    main()