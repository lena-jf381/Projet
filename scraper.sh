#!/bin/bash

url="https://wise.com/fr/stock/aapl"

price=$(curl -s $url | grep -oP '(?<=<div class="mw-display-3 m-b-1">)[^<]+' | head -n 1)

echo "$price"
