#!/bin/bash

url="https://wise.com/fr/stock/aapl"

PRICE=$(curl -s $URL | grep -oP '(?<=<div class="mw-display-3 m-b-1">)[^<]+' | head -n 1)

echo "Nombre total de cas : $PRICE"
