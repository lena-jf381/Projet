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

Pour que ce programme fonctionne, il faut des données en local. L'application vous proposera de les télécharger sur notre VM si vous n'avez pas lancé scraper.sh

Pour configurer le scraper, il vous faut effectuer les opérations suivantes : 

```bash
crontab -e

*/5 * * * * cd /home/azureuser/projetlinux/Projet && /home/azureuser/projetlinux/Projet/scraper.sh
0 20 * * * cd /home/azureuser/projetlinux/Projet && /home/azureuser/projetlinux/Projet/report_generation.sh
```