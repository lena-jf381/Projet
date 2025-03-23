#!/bin/bash

url="https://wise.com/fr/stock/"

get_valeur(){
    price=$(curl -s $url$2 | grep -oP '(?<=<div class="mw-display-3 m-b-1">)[^<]+' | head -n 1)
    #Récupère la date et le prix. Sauvegarde dans un fichier avec le nom de l'entreprise en minuscule 
    echo "$(date '+%d/%m/%Y %H:%M:%S');$price" >> data_$(echo $1 |  tr '[A-Z]' '[a-z]').csv
}

get_valeur "APPLE" "aapl"
get_valeur "MICROSOFT" "msft"
get_valeur "AMAZON" "amzn"
get_valeur "Google" "googl"