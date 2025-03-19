#!/bin/bash

# URL du site à scraper
url="https://www.worldometers.info/coronavirus/"

# Scraping pour obtenir le nombre de cas totaux
cas=$(curl -s $url | grep -oP '(?<=<span style="color:#aaa">)[0-9,]+' | head -n 1)


echo "Nombre total de cas : $cas"
