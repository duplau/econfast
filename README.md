
# Guide d'utilisation

__Recherche__

Il suffit de saisir un ou plusieurs termes de recherche :
- nom et/ou prénom d'économiste
- institution d'affiliation (université, association, etc.)
- mots-clefs thématiques
- expressions, mots ou concepts caractérisant le sujet de recherche.

Ces types de termes peuvent être combinés, toutefois l'application renvoie toujours un ou plusieurs auteurs comme résultats de recherche.

__Résultats__

Pour chaque auteur correspondant à la requête, il est possible de cliquer sur ce résultat afin d'afficher un profil sommaire et de parcourir ses publications. 

Le profil permet de naviguer vers une page professionnelle ("homepage") de l'économiste en question, quand celle-ci est disponible. Cette page contient souvent une notice biographique, aussi le lien s'appelle-t-il "Biographie".

Le profil indique également de façon synthétique les économistes les plus proches de l'auteur considéré, la proximité étant calculée simplement à partir du nombre de co-publications. Ce "réseau de plus proches co-auteurs" est représenté par une visualisation très basique en graphe.

La navigation parmi les publications se fait via les boutons _Publi suivante_ et _Publi précédente_, ou au clavier par les flèches gauche et droite ; l'utilisateur peut cliquer sur le titre d'une publication pour l'ouvrir dans son navigateur ; enfin, on revient aux résultats de recherche (ou à une nouvelle recherche) en cliquant sur le bouton _Fermer_ (ou via la touche d'échappement).

# Installation

Le processus d'installation et d'exécution de EconFast peut être décomposé en 3 phases :

### 1. Dataprep (préparation des données)

Il s'agit de la phase préalable de transformation et traitement des données sources, réalisée au moment de la conception et de l'écriture de l'outil (et donc pas à réitérer lors de l'installation de l'outil, contrairement à la phase suivante).

Elle contient les étapes nécessaires à la gestion des synonymes et la fonctionnalité d'auto-complétion, chacune décrite dans une section par la suite.
- Pour les synonymes, le script `build_synonyms_inst.sh` est exécuté.
- Pour l'auto-complétion, les listes d'institutions enregistrées dans la base EDIC, d'auteurs les plus populaires, et de thématiques JEL sont simplement converties en objets JSON pour servir de cibles d'auto-complétion.
  - La liste d'auteurs est constituée en exécutant la commande `python3 find_top_authors.py | grep -v "†" | sort | uniq > top_authors` (les URLs des pages personnelles de ces chercheurs sont glanées au passage)
  - Les listes d'institutions et de thématiques sont simplement téléchargées sans autre traitement

### 2. Installation logicielle

a. installer un gestionnaire de packages (tel que homebrew sur MacOS)
b. installer les deux seules dépendances logicielles
  - wget (pour le téléchargement des données REPeC)
  - Docker (pour la Docker machine, incluant docker-compose)
c. télécharger les données REPeC en exécutant dans le répertoire `econ_fast/repec_data/data` : `wget -r -c -N -np -nH -A "*.rdf" --cut-dirs=3 -R index.html ftp://ftp.repec.org/opt/ReDIF/RePEc/`

### 3. Exécution

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

### _Scraping_ d'images

L'outil réalise du _scraping_ des résultats de Google Image Search afin de glaner deux types d'images : portraits d'économistes et logos d'institutions.

- __Photos des auteurs__ : nous avons implémenté dans EconSearch un module d'analyse des images résultantes de recherches Google Image Search afin de garantir que soient indexées des portraits des économistes. En d'autres termes, il s'agit de s'assurer que ces images correspondent à un (unique) visage de face, autrement dit une photo adaptée au profil du chercheur en question (alors qu'un nombre minime mais non négligeable d'images parmi les premiers résultats sont soit une photo de groupe, soit une photo de pied, ou quelques autres variantes). Un tel filtre a été implémenté dans le fichier `image_analysis.py` et est assez optimisé pour être exécuté en parallèle de l'indexation des données du moteur de recherche.

Le code associé au _scraping_ d'images est dans le fichier `image_crawl.py`, il est très simple mais contient quelques heuristiques permettant de mieux cibler les résultats et d'exclure les images non-pertinentes telles que le carrousel d'images associées dans Google Search.



# Détails techniques

### Architecture

De façon classique, l'outil EconFast se compose d'une base de données, d'un backend et d'un frontend.

__La base de données__ est une instance ElasticSearch (ES) qui contient deux index : un pour les publications et un pour les auteurs. Au moment de l'indexation, des images sont récupérées depuis Google Image Search. C'est la seule partie de scraping proprement dite dans l'outil, car le reste des données (REPeC ou autres sources) sont récupérées par un simple téléchargement. Le peuplement de la base ES est assuré par une variété de scripts se trouvant dans le répertoire racine du repo github du projet.

__Le backend__ est composé d'une API REST très basique implémentée en Node.js, avec deux verbes `/search` et `/publi` pour récupérer respectivement les résultats de recherche d'auteurs et une publication particulière. Son code est dans le répertoire `server` du repo github du projet.

__Le front-end__ est une application Vue.js de type _single-page app_. Son code est dans le répertoire `public` du repo github du projet. Noter que tous les éléments de ce front-end, y compris le composant d'auto-suggestion, ont été écrits en pur Vue.js, sans utiliser de librairie tierce-partie, par souci de simplicité.

L'ensemble est livré sous forme de 3 conteneurs Docker :
- un conteneur pour l'instance ES
- un conteneur pour le serveur Node.js
- un conteneur pour le front-end Vue.js
Ils peuvent être étendus à 4 en ajoutant un simple composant nginx faisant office de reverse proxy pour une meilleur tenue en charge (ce qui ne s'est pas avéré nécessaire lors de nos tests de montée en charge).

### Principes de conception


Quelques principes ont été suivis pour concevoir et implémenter cet outil :

1. __Concision et clarté__
	- Le code a été écrit en privilégiant la concision sur la maintenabilté.
	- En effet il s'agit d'un prototype et comme on le sait, tout prototype (surtout réalisé dans le cadre d'un hackathon est au mieux destiné à être refactorisé).
2. __Méthodologie innovante__
	- L'outil traite de gros volumes de données structurées (champs prédéfinis) et non structurées (texte des publications), sans toutefois relever du Big Data et en demeurant en mode batch (pas de traitement en temps réel).
	- L'innovation de notre méthodologie réside dans la sélection et l'assemblage d'algorithmes ad-hoc pour traiter ces données : lignes de commande Unix relationnelles pour leur préparation, parsing léger pour leur transformation, base de données NoSQL pour l'indexation du texte, crawling des images au moment de l'indexation. 
	- Le tout en opérant des arbitrages entre exhaustivitée et faisabilité des traitements : par exemple les photos identifiant les chercheurs sont récupérées pour les auteurs les plus populaires uniquement, etc. 
3. __Capacités d'intégration__
	- L'architecture de l'outil est basé sur des conteneurs Docker, donc 100% portables et rendant l'installation triviale sur toute machine virtuelle, assemblés via docker-compose (noter qu'une première version plus complexe utilisait Kubernetes pour orchestrer les divers services, mais cela s'est avéré superflu et rendant le déploiement inutilement complexe).
	- Par ailleurs, des tests ont été réalisés en utilisant plusieurs instances ElasticSearch, mais le gain en vitesse d'indexation ou de recherche n'était pas significatif. 
4. __Acceptabilité technique et éthique__
	- L'utilisation des données REPeC est faite par un simple téléchargement (c'est même la raison d'être de REPeC que de fournir cet accès via plusieurs sites miroirs).
	- Quant aux résultats de Google Image Search, il s'agit d'image accessibles publiquement et le scraping est maîtrisé afin de rester dans les quotas imposés par Google (https://developers.google.com/webmaster-tools/search-console-api-original/v3/limits), soit 50 requêtes/s et 1200 requêtes/min. Noter que cette restriction ("throttling" en anglais) est assurée par le processus de sélection des images à récupérer : il s'agit uniquement des auteurs les plus populaires ("top authors" tels que définis par REPeC, cf. https://ideas.repec.org/top/top.person.all.html) et des institutions ayant le plus publié (tel que calculé par nos propres soins, lorsque le flag `COMPUTE_TOP_INSTITUTIONS` est positionné à `True` dans le script d'indexation des publications). 

# Améliorations futures

Comme dans tout projet de hackathon, l'exercice de conception et implémentation, limité dans le temps par définition, a mis au jour de nombreuses pistes d'évolutions futures. Parmi celles-ci :

- __Logos des institutions__ : filtrer les images récoltées parmi les résultats Google Image Search afin de s'assurer que celles-ci représentent un logo d'institution (universitaire, privée, gouvernementale, etc.). Un filtre minimaliste consiste à inclure uniquement les images polychromatiques. Comme pour le filtre des photos d'auteurs, celui-ci a été implémenté dans le fichier `image_analysis.py`, mais pas activé dans les paramètres par défaut car l'analyse de chaque image est chronophage.
- __Normalisation des intitulés d'institutions__ : parmi les 176 477 intitutlés uniques, le but est de dédoublonner aussi finement que possible, ce qui nécessite de construire une taxonomie hiérarchique (par exemple, University of Pennsylvania est une institution mère de la Wharton School). La première étape se fait par un algorithme itératif simple tel que celui-ci :
  1. fusionner les intitulés différant seulement par des caractères vides (whitespace)
  2. si C = "A and B" alors supprimer C
  3. fusionner C en A lorsque A est un préfixe de C suffisamment descriptif (i.e. en supprimant l'information redondante telle que nom de ville ou abréviation de l'institution)
  4. itérer les étapes 1-3

# Détails techniques

### Volumétrie

Les données suivantes sont indexées, et donc requêtables, dans EconFast :
- 6 354 032 publications
- 1 012 467 auteurs, comprenant les 57 000 enregistrés dans REPeC (une majorité sont des auteurs "mineurs" au sens qu'ils n'ont publié qu'un article et ne sont pas affiliés à une institution officielle : cette situation est une conséquence de l'ouverture des données REPeC, à laquelle nous avons pallié en privilégiant les auteurs influe nts et les institutions enregistrées dans l'EDIC)
- 4,657 institutions, dans 232 pays (selon l'EDIC), normalisées à partir de 176 477 dénominations uniques d'institutions
- 869 thèmes JEL

### Configuration ElasticSearch

- On positionne le timeout des scans à 60min (car l'indexation des auteurs prend un temps considérable, plusieurs heures sur une bonne machine)
- Pour les _circuit breaker settings_ (https://www.elastic.co/guide/en/elasticsearch/reference/current/circuit-breaker.html), on positionne le flag `indices.breaker.total.use_real_memory = False`

### Gestion des synonymes

On traite deux sortes de synonymes :
- les équivalences français-anglais des noms de thématiques (du moins JEL). Cela permet par exemple de chercher une thématique en français telle que "Santé et inégalités", ce qui remontera non seulement les articles publiés en français traitant de cette thématique, mais aussi ceux catégorisés sous la classification JEL "I14 - Health and Inequality" ainsi que ceux publiés uniquement en anglais et traitant de ce sujet.
- les acronymes et autres initialismes associés à une institution. Cela permet par exemple de remonter les publications de chercheurs affiliés à la LSE, que les termes de recherche saisis incluent "LSE" ou "London School of Economics"

### Auto-complétion

Le composant d'auto-complétion a été intégralement écrit en Vue.js (pas de librairie ou code tierce-partie pour cette fonctionnalité).

Des suggestions sont proposées en fonction des caractères saisis dans la barre de recherche, qui peuvent être de trois types :
* institutions (5773 possibilités : les institutions enregistrées dans la base EDIC)
* auteurs (5555 possibilités : les chercheurs les plus populaires)
* thématiques (859 possibilités : toutes les thématiques JEL)
