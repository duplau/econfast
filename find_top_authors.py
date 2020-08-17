# -*- coding: utf-8 -*-

import re, requests
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

'''
Ce script permet de constituer la liste "à plat" des auteurs les plus populaires 
à partir de la liste maintenue par REPeC et disponible sur https://ideas.repec.org/top/top.person.all.html. 

Il est destiné à être exécuté une seule fois, et doit l'être avant l'indexation des auteurs.
'''

AUTHOR_RE = re.compile(r"/[a-z]/[a-z]{3}[0-9]{1,3}.html")

def fetch_author_info(url):
	response = requests.get("https://ideas.repec.org" + url)
	soup = BeautifulSoup(response.content, 'lxml')
	tags = soup.find_all("td", {"class": "homelabel"})
	if len(tags) == 1:
		daddy = tags[0].parent
		next_tag = daddy.findNext("td").findNext("td")
		if next_tag:
			return next_tag.text
	return None

with open("backup/top.person.all.html") as f:
    soup = BeautifulSoup(f, "html.parser")
    authors = soup.find_all('a', {'href': AUTHOR_RE})
    for author in authors:
    	full_name = author.text
    	author_page = author.get("href")
    	homepage = fetch_author_info(author_page)
    	print("|".join([full_name, homepage if homepage else ""]))
