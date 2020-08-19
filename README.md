
# Installation

Le processus d'installation et d'exécution de EconFast peut être décomposé en 3 phases :

1. Dataprep (préparation des données)

Il s'agit de la phase préalable de transformation et traitement des données sources, réalisée au moment de la conception et de l'écriture de l'outil (et donc pas à réitérer lors de l'installation de l'outil, contrairement à la phase suivante).

Elle contient les étapes nécessaires à la gestion des synonymes et la fonctionnalité d'auto-complétion, chacune décrite dans une section par la suite.
- Pour les synonymes, le script `build_synonyms_inst.sh` est exécuté.
- Pour l'auto-complétion, les listes d'institutions enregistrées dans la base EDIC, d'auteurs les plus populaires, et de thématiques JEL sont simplement converties en objets JSON pour servir de cibles d'auto-complétion.
  - La liste d'auteurs est constituée en exécutant la commande `python3 find_top_authors.py | grep -v "†" | sort | uniq > top_authors` (les URLs des pages personnelles de ces chercheurs sont glanées au passage)
  - Les listes d'institutions et de thématiques sont simplement téléchargées sans autre traitement

2. Installation logicielle

a. installer un gestionnaire de packages (tel que homebrew sur MacOS)
b. installer les deux seules dépendances logicielles
  - wget (pour le téléchargement des données REPeC)
  - Docker (pour la Docker machine, incluant docker-compose)
c. télécharger les données REPeC en exécutant dans le répertoire `econ_fast/repec_data/data` : `wget -r -c -N -np -nH -A "*.rdf" --cut-dirs=3 -R index.html ftp://ftp.repec.org/opt/ReDIF/RePEc/`

3. Exécution

Il ne reste qu'à :
- compiler et lancer le service EconFast en exécutant dans le répertoire `econ_fast` : `docker-compose up --build`
- indexer les données, en exécutant dans le répertoire `econ_fast` : `./instal_all` ce qui crée les deux index décrits dans la section architecture ci-dessous, contenant l'ensemble des données REPeC après pré-traitements ainsi que les images issues du scraping de Google Image Search. 

# Description de quelques fonctionnalités

### Gestion des synonymes

On traite deux sortes de synonymes :
- les équivalences français-anglais des noms de thématiques (du moins JEL). Cela permet par exemple de chercher une thématique en français telle que "Santé et inégalités", ce qui remontera non seulement les articles publiés en français traitant de cette thématique, mais aussi ceux catégorisés sous la classification JEL "I14 - Health and Inequality" ainsi que ceux publiés uniquement en anglais et traitant de ce sujet.
- les acronymes et autres initialismes associés à une institution. Cela permet par exemple de remonter les publications de chercheurs affiliés à la LSE, que les termes de recherche saisis incluent "LSE" ou "London School of Economics"

### Auto-complétion

Des suggestions sont proposées en fonction des caractères saisis dans la barre de recherche, qui peuvent être de trois types :
* institutions (5773 possibilités : les institutions enregistrées dans la base EDIC)
* auteurs (5555 possibilités : les chercheurs les plus populaires)
* thématiques (859 possibilités : toutes les thématiques JEL)

# Architecture de l'outil

De façon classique, il se compose d'une base de données, d'un backend et d'un frontend.

__La base de données__ est une instance ElasticSearch (ES) qui contient deux index : un pour les publications et un pour les auteurs. Au moment de l'indexation, des images sont récupérées depuis Google Image Search. C'est la seule partie de scraping proprement dite dans l'outil, car le reste des données (REPeC ou autres sources) sont récupérées par un simple téléchargement. Le peuplement de la base ES est assuré par une variété de scripts se trouvant dans le répertoire racine du repo github du projet.

__Le backend__ est composé d'une API REST très basique implémentée en Node.js, avec deux verbes `/search` et `/publi` pour récupérer respectivement les résultats de recherche d'auteurs et une publication particulière. Son code est dans le répertoire `server` du repo github du projet.

__Le front-end__ est une application Vue.js de type _single-page app_. Son code est dans le répertoire `public` du repo github du projet. Noter que tous les éléments de ce front-end, y compris le composant d'auto-suggestion, ont été écrits en pur Vue.js, sans utiliser de librairie tierce-partie, par souci de simplicité.

L'ensemble est livré sous forme de 3 conteneurs Docker (un conteneur pour l'instance ES, un pour le serveur Node.js, et un pour le front-end Vue.js), qui peuvent être étendus à 4 en ajoutant un simple composant nginx faisant office de reverse proxy pour une meilleur tenue en charge (ce qui ne s'est pas avéré nécessaire lors de nos tests de montée en charge).

## Caractéristiques de l'outil

- propreté du code : le code a été écrit en privilégiant la concision sur la maintenabilté. Il s'agit d'un prototype et comme on le sait, tout prototype (surtout réalisé dans le cadre d'un hackathon est au mieux destiné à être refactorisé).

- innovation

- facilité d'intégration : l'architecture de l'outil est basé sur des conteneurs Docker, donc 100% portables et rendant l'installation triviale sur toute machine virtuelle, assemblés via docker-compose (noter qu'une première version plus complexe utilisait Kubernetes pour orchestrer les divers services, mais cela s'est avéré superflu et rendant le déploiement inutilement complexe). Par ailleurs, des tests ont été réalisés en utilisant plusieurs instances ElasticSearch, mais le gain en vitesse d'indexation ou de recherche n'était pas significatif. 

- éthique : l'utilisation des données REPeC est faite par un simple téléchargement (c'est même la raison d'être de REPeC que de fournir cet accès via plusieurs sites miroirs). Quant aux résultats de Google Image Search, il s'agit d'image accessibles publiquement et le scraping est maîtrisé afin de rester dans les quotas imposés par Google (https://developers.google.com/webmaster-tools/search-console-api-original/v3/limits), soit 50 requêtes/s et 1200 requêtes/min. Noter que cette restriction ("throttling" en anglais) est assurée par le processus de sélection des images à récupérer : il s'agit uniquement des auteurs les plus populaires ("top authors" tels que définis par REPeC, cf. https://ideas.repec.org/top/top.person.all.html) et des institutions ayant le plus publié (tel que calculé par nos propres soins, lorsque le flag `COMPUTE_TOP_INSTITUTIONS` est positionné à `True` dans le script d'indexation des publications). 


# Guide d'utilisation

__Recherche__

Saisir des termes de recherche :
- nom et/ou prénom d'auteur
- institution (université, association, etc.)
- mots-clefs thématiques
Ces types de termes peuvent être combinés, toutefois l'application renvoie toujours un ou plusieurs auteurs comme résultats de recherche.

__Résultats__

Pour chaque auteur correspondant à la requête, il est possible de cliquer sur ce résultat afin d'afficher un profil sommaire et de parcourir ses publications. 
La navigation parmi les publications se fait via les boutons _Publi suivante_ et _Publi précédente_, ou au clavier par les flèches gauche et droite ; l'utilisateur peut cliquer sur le titre d'une publication pour l'ouvrir dans son navigateur ; enfin, on revient aux résultats de recherche (ou à une nouvelle recherche) en cliquant sur le bouton _Fermer_ (ou via la touche d'échappement).





# Améliorations futures

Comme dans tout projet de hackathon, l'exercice de conception et implémentation, limité dans le temps par définition, a mis au jour de nombreuses pistes d'évolutions futures. Parmi celles-ci :

- Photos des auteurs : filtrer les photos récoltées parmi les résultats Google Image Search afin de s'assurer que celles-ci correspondent à un (unique) visage de face, autrement dit une photo adaptée au profil du chercheur en question (alors qu'un nombre minime mais non négligeable d'images parmi les premiers résultats sont soit une photo de groupe, soit une photo de pied, ou quelques autres variantes). Un tel filtre a été implémenté dans le fichier `image_analysis.py`, mais pas activé dans les paramètres par défaut car l'analyse de chaque image est chronophage.
- Logos des institutions : filtrer les images récoltées parmi les résultats Google Image Search afin de s'assurer que celles-ci représentent un logo d'institution (universitaire, privée, gouvernementale, etc.). Un filtre minimaliste consiste à inclure uniquement les images polychromatiques. Comme pour le filtre des photos d'auteurs, celui-ci a été implémenté dans le fichier `image_analysis.py`, mais pas activé dans les paramètres par défaut car l'analyse de chaque image est chronophage.

----

# Install procedure (on MacOS 10.15!)

```sh
install homebrew
install wget
# TODO also accept *.redif
wget -r -c -N -np -nH -A "*.rdf" --cut-dirs=3 -R index.html ftp://ftp.repec.org/opt/ReDIF/RePEc/
install Docker (includes docker-compose)
```


# Volumétrie
- publications
- 57,000 authors have registered on REPeC (on my test sample: for 886 472 publications, 835 869 authors)
- 4,657 institutions in 232 countries and territories (as per EDIC) vs. 68384 unique names found in EDI files
- thèmes JEL

Rem: count represents the number of documents indexed in your index while index_total stands for number of indexing operations performed during elasticsearch uptime. We will observe doc, so to count indexed publications one can fetch URL `http://localhost:9200/publication/_stats`, and to count indexed authors `http://localhost:9200/author/_stats`.

# Dataprep

__Institutions__: initially 176477 string names for attribute Author-Workplace-Name.
Goal is to dedupe as close to 4657 as possible.

i. merge when differ only by whitespace
ii. if C = "A and B" then remove C
iii. merge C into A when A is a prefix of C (descriptive enough, removes redundant info like the city name, the abbreviation, etc.)
iv. iterate 3 times on (i) then (ii) then (iii)

__Author names__: RD to describe

# TODOs & bugs

TODO: check that acronyms work correctly (e.g. OECD returns first and foremost papers published by the OECD)

BUG, hopefully fixed: index_authors.py fails with
```
WARNING:elasticsearch:GET http://localhost:9200/author/_doc/gMX21HMB3J4LOXHFGlVt [status:429 request:0.010s]
WARNING:elasticsearch:DELETE http://localhost:9200/_search/scroll [status:429 request:0.001s]
Exception ignored in: <generator object scan at 0x10ef4e9a8>
Traceback (most recent call last):
  File "/Library/Python/3.7/site-packages/elasticsearch/helpers/actions.py", line 531, in scan
    client.clear_scroll(body={"scroll_id": [scroll_id]}, ignore=(404,))
  File "/Library/Python/3.7/site-packages/elasticsearch/client/utils.py", line 139, in _wrapped
    return func(*args, params=params, headers=headers, **kwargs)
  File "/Library/Python/3.7/site-packages/elasticsearch/client/__init__.py", line 454, in clear_scroll
    "DELETE", "/_search/scroll", params=params, headers=headers, body=body
  File "/Library/Python/3.7/site-packages/elasticsearch/transport.py", line 352, in perform_request
    timeout=timeout,
  File "/Library/Python/3.7/site-packages/elasticsearch/connection/http_urllib3.py", line 256, in perform_request
    self._raise_error(response.status, raw_data)
  File "/Library/Python/3.7/site-packages/elasticsearch/connection/base.py", line 288, in _raise_error
    status_code, error_message, additional_info
elasticsearch.exceptions.TransportError: TransportError(429, 'circuit_breaking_exception', '[parent] Data too large, data for [<http_request>] would be [511649004/487.9mb], which is larger than the limit of [510027366/486.3mb], real usage: [511648728/487.9mb], new bytes reserved: [276/276b], usages [request=0/0b, fielddata=0/0b, in_flight_requests=276/276b, accounting=243540/237.8kb]')
Traceback (most recent call last):
  File "index_authors.py", line 161, in <module>
    index_authors_from_publis()
  File "index_authors.py", line 109, in index_authors_from_publis
    obj = ES.get(index=ES_INDEX_AUTHOR, id=aid)
  File "/Library/Python/3.7/site-packages/elasticsearch/client/utils.py", line 139, in _wrapped
    return func(*args, params=params, headers=headers, **kwargs)
  File "/Library/Python/3.7/site-packages/elasticsearch/client/__init__.py", line 975, in get
    "GET", _make_path(index, doc_type, id), params=params, headers=headers
  File "/Library/Python/3.7/site-packages/elasticsearch/transport.py", line 352, in perform_request
    timeout=timeout,
  File "/Library/Python/3.7/site-packages/elasticsearch/connection/http_urllib3.py", line 256, in perform_request
    self._raise_error(response.status, raw_data)
  File "/Library/Python/3.7/site-packages/elasticsearch/connection/base.py", line 288, in _raise_error
    status_code, error_message, additional_info
elasticsearch.exceptions.TransportError: TransportError(429, 'circuit_breaking_exception', '[parent] Data too large, data for [<http_request>] would be [511648728/487.9mb], which is larger than the limit of [510027366/486.3mb], real usage: [511648728/487.9mb], new bytes reserved: [0/0b], usages [request=0/0b, fielddata=0/0b, in_flight_requests=0/0b, accounting=243540/237.8kb]')
```

curl localhost:9200/_cluster/settings?include_defaults&flat_settings&local&filter_path=defaults.indices*


# Useful stuff

Retrieve a publication by its pub_id : `http://localhost:9200/publication/_doc/E0sAvnMBFHsL7LaCJGMf`

Find authors for which the field current_institution is defined: 

	curl -X GET "localhost:9200/author/_search?pretty" -H 'Content-Type: application/json' -d'
	{
	  "query": {
	    "exists": {
	      "field": "current_institution"
	    }
	  }
	}
	'

# ES config

- On positionne le timeout des scans à 60min (car l'indexation des auteurs prend un temps considérable, plusieurs heures sur une bonne machine)
- Pour les _circuit breaker settings_ (https://www.elastic.co/guide/en/elasticsearch/reference/current/circuit-breaker.html), on positionne le flag `indices.breaker.total.use_real_memory = False`

# Gestion des synonymes

On traite deux sortes de synonymes :
- les équivalences français-anglais des noms de thématiques (du moins JEL). Cela permet par exemple de chercher une thématique en français telle que "Santé et inégalités", ce qui remontera non seulement les articles publiés en français traitant de cette thématique, mais aussi ceux catégorisés sous la classification JEL "I14 - Health and Inequality" ainsi que ceux publiés uniquement en anglais et traitant de ce sujet.
- les acronymes et autres initialismes associés à une institution. Cela permet par exemple de remonter les publications de chercheurs affiliés à la LSE, que les termes de recherche saisis incluent "LSE" ou "London School of Economics"

# Auto-complétion

- Des suggestions sont proposées en fonction des caractères saisis dans la barre de recherche, qui peuvent être de trois types :
	* institutions (5773 possibilités : les institutions enregistrées dans la base EDIC)
	* auteurs (5555 possibilités : les chercheurs les plus populaires)
	* thématiques (859 possibilités : toutes les thématiques JEL)

# Divers petits scripts

#### Assemble list of top authors
* Save https://ideas.repec.org/top/top.person.all.html
* Run `python3 find_top_authors.py > top_authors`


#### Traitement des codes et étiquettes JEL

```sh
awk 'BEGIN{FS="\t"; OFS="|"} NF>1{a=$1; $1=""; print $0, a}' < jel_v0 > jel_v1
```

#### Conversion de listes (un item par ligne) en tableau JS

awk '{print "\"" $0 "\"," }' < suggest_institutions > suggest_institutions.js
awk '{print "\"" $0 "\"," }' < tmp > suggest_authors.js
awk '{print "\"" $0 "\"," }' < synonyms_inst > synonyms.js

#### Production des initialismes de noms d'institutions

awk 'BEGIN{ FS=" " } { if ($NF~ /\([A-Z]+\)/) { acro = substr($NF, 2, length($NF)-2); $NF=""; NF-=1; print acro " => " $0 } else if ($(NF-1) == "-") { acro = $NF; $NF=""; $(NF-1)=""; NF-=2; print acro " => ", $0 } }' < registered_institutions | sort | uniq > synonyms_inst

# Détails techniques


- Stack technique et architecture : 3 composants Docker (serveur node / instance ElasticSearch / front-end Vue.js), qui peuvent être étendus à 4 en ajoutant un simple composant nginx faisant office de reverse proxy pour une meilleur tenue en charge.
- The auto-suggest component was built in pure Vue (no 3rd-party library for that feature), see https://www.digitalocean.com/community/tutorials/vuejs-vue-autocomplete-component
