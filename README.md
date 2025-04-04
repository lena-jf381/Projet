# Projet Linux

Pour installer notre projet, créé un virtual env python >=3.11
```python
python -m venv .venv
```

Activer l'environnement virtuel en exécutant la commande suivante sur linux
```bash
source .venv/bin/activate
```
Sur windows
```cmd
.venv/scripts/activate
```

Mettre à jour pip
```cmd
python.exe -m pip install --upgrade pip
```

Récupérez les modules pythons en tapant
```bash
pip install -r requirements.txt
```

Attention, pour que ce programme fonctionne en local, il faut des fichiers contenant les valeurs d'actions technologiques. Ces fichiers sont générés par le programme scraper.sh qu'il faut configurer dans le crontab de la façon suivante

```bash
crontab -e

*/5 * * * * cd /home/azureuser/projetlinux/Projet && /home/azureuser/projetlinux/Projet/scraper.sh
```