import re
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

'''
Ce script permet de constituer la liste "à plat" des auteurs les plus populaires 
à partir de la liste maintenue par REPeC et disponible sur https://ideas.repec.org/top/top.person.all.html. 

Il est destiné à être exécuté une seule fois, et doit l'être avant l'indexation des auteurs.
'''

AUTHOR_RE = re.compile(r"/[a-z]/[a-z]{3}[0-9]{1,3}.html")

with open("top.person.all.html") as f:
    soup = BeautifulSoup(f, "html.parser")
    images = soup.find_all('a')
    images = soup.find_all('a', {'href': AUTHOR_RE})
    for image in images:
        print(image.text)
