#!/bin/bash

url="https://www.worldometers.info/coronavirus/"

cas=$(curl -s $url | grep -oP '(?<=<span style="color:#aaa">)[0-9,]+' | head -n 1)

echo "Nombre total de cas : $cas"
