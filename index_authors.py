#!/usr/bin/python3
import re, io, glob, logging, sys
import normalize_institutions, image_crawl
from pathlib import Path
from collections import defaultdict, Counter
from multiprocessing import Pool
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk, scan

# Position this flag to False if you wish to build a quick index, without images (author pictures and institution logos)
CRAWL_IMAGES = True

logging.basicConfig(level=logging.WARNING)

ES_PORT = 9200

ES_INDEX_PUBLI = 'publication'

ES_INDEX_AUTHOR = 'author'

'''
	ES mapping used for the author index.
'''	
MAPPING_AUTHOR = {
	"settings": {
		"number_of_shards": 1,
		# Use at least for authors
		# Maybe for institutions? (although we do want to discount very large universities)
		"similarity": {
		  "tf_sim": {
		    "type": "scripted",
		    "script": {
		      "source": "double tf = Math.sqrt(doc.freq); double norm = 1/Math.sqrt(doc.length); return query.boost * tf * norm;"
		    }
		  }
		}
	},
	"mappings": {
		"properties": {
			# Full name as found in the ReDIF file
			"full_name": { "type": "text", "similarity": "tf_sim" },
			# Aliases are just used to pick the best full name
            "aliases": { "type": "text", "index": False },
            # Author homepage
            "home_url": { "type": "text", "index": False },
            # List of institutions (appear n times if n publications signed by this author when affiliated to that institution)
			"institutions": { "type": "text" },

			# List of topics (in English, not the JEL codes!), appear n times if n papers published by this author on that JEL topic 
			# "specialties": { "type": "text" },
			# List of topics (in French, not the JEL codes!), appear n times if n papers published by this author on that JEL topic 
			# "specialites": { "type": "text" },

			"show_specialites": { "type": "text", "index": False },
			# List of topics as keywords, appear n times if n papers published by this author with that keyword
			"keywords": { "type": "text" },
			# List of publication titles
			"titles": { "type": "text" },
			# List of abstract texts
			"abstracts": { "type": "text" },
			# Last known affiliation
			"current_institution": { "type": "text" },
			# Latest publication seen
			"latest_pub_date": { "type": "text" },
			# List of pairs (pub_id, pub_date)
			"pub_ids": { "type": "nested" }
		}
	}
}

ES = Elasticsearch()

ENCODINGS = ['utf-8', 'utf-16-le']

def lines(f):
	handle = None
	for e in ENCODINGS:
		if handle:
			handle.close()
			break
		try:
			handle = io.open(f, 'r', encoding=e)
			for l in handle:
				yield l.strip()
		except:
			logging.debug("Error opening file {} in {}".format(f, e), sys.exc_info()[0])

def valid_pubdate(t):
	return t["pub_date"] if "pub_date" in t and t["pub_date"] else "2020-08"

def remove_comma(n):
	l = list([i.strip() for i in n.split(",")])
	if len(l) < 2:
		return n
	if len(l) > 2:
		logging.warning("Found full name with several commas: {}".format(n))
	return l[1] + " " + l[0]	

def hash_name(n):
	if len(n) < 4:
		return None
	m = remove_comma(n)
	l = list([i.lower().strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 0])
	if len(l) > 0:
		for i in range(1, len(l)-1):
			l[i] = l[i][0]
		return " ".join(l)
	return None

'''
	Picks the best variant among several full names for the same person.
	
	The best variant first maximizes the token count, then maximizes the number of full tokens (as 
	opposed to initials), finally minimizes the number of commas.
	
	For example with "Harvey, Andrew C.", "Andrew C. Harvey", "Andrew Harvey", "Andrew Charles Harvey", 
	the latter will be selected.
'''
def best_name_variant(names):
	best = sorted(names, key=name_variant_key, reverse=True)[0]
	return " ".join([i[0].upper() + (i[1:].lower() if len(i) > 1 else "") for i in best.split(" ") if len(i) > 0])

'''
	Used to sort name variants when picking the best one.
'''	
def name_variant_key(n):
	return metric_token_count(n), metric_full_token_count(n), metric_comma_count(n)

'''
	1st metric to select the best name variant
'''	
def metric_token_count(n):
	m = remove_comma(n)
	l = list([i.strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 0])
	return len(l)

'''
	2nd metric to select the best name variant
'''	
def metric_full_token_count(n):
	m = remove_comma(n)
	l = list([i.strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 1])
	return len(l)

'''
	3rd metric to select the best name variant
'''	
def metric_comma_count(n):
	return 0 if n.count(",") > 0 else 1

TOP_AUTHORS = dict()
for l in lines('top_authors'):
	items = list([i.strip() for i in l.split("|")])
	if len(items) != 2:
		logging.error("Invalid author row: {}".format(l))
	name_hash = hash_name(items[0])
	home_url = items[1]
	TOP_AUTHORS[name_hash] = home_url
logging.info("Loaded {} top authors".format(len(TOP_AUTHORS)))

# Mapping from author ID (name hash) to counter of JEL code frequencies
AUTHOR_SPECIALTIES = defaultdict(Counter)

TOP_INSTITS = set(lines("top_institutions"))
logging.info("Loaded {} top institutions".format(len(TOP_INSTITS)))

# Mapping from an institution's name to its logo
INST_LOGOS = dict()

"""
	If settings include image crawling, this method will either fetch an already scraped institution's logo 
	or will scrape it from Google Image Search results.
"""	
def fetch_logo(inst, obj):
	if CRAWL_IMAGES: # and inst in TOP_INSTITS:
		inst_hash = normalize_institutions.hash_institution(inst)
		if inst_hash not in INST_LOGOS:
			query_str = ' '.join(inst.split("-")[:2])
			logo_urls = list(image_crawl.yield_image_urls(["logo", query_str]))
			INST_LOGOS[inst_hash] = logo_urls
		else:
			logo_urls = INST_LOGOS[inst_hash]
		if len(logo_urls) > 0:
			obj["logo_urls"] = logo_urls

'''
	Indexing method used for a publication author who is already in  the authors index.

	In this case, its JEL labels / specialties attributes are updated, along with its publication list,
	and the current affiliation if needed.
'''
def index_existing_author(publi, pub_tuple, author, aid_by_hash, full_name, name_hash):
	logging.debug("Already existing author: {} --> {}".format(full_name, name_hash))
	aid = aid_by_hash[name_hash]
	obj = ES.get(index=ES_INDEX_AUTHOR, id=aid)
	upd_author = { }
	old_author = obj["_source"]
	if full_name not in old_author["aliases"]:
		upd_author["aliases"] = old_author["aliases"] + [full_name]
		upd_author["best_name"] = best_name_variant(upd_author["aliases"])
		logging.debug("Picked best variant {} among {}".format(upd_author["best_name"], upd_author["aliases"]))
	if "institution" in author:
		inst = author["institution"]
		upd_author["institutions"] = inst + " " + old_author["institutions"]
		if "creation-date" in publi:
			if "latest_pub_date" not in old_author or old_author["latest_pub_date"] < publi["creation-date"]:
				upd_author["current_institution"] = inst
				upd_author["latest_pub_date"] = publi["creation-date"]
				fetch_logo(inst, upd_author)
	if "jel-labels-en" in publi:
		upd_author["jel-labels-en"] = old_author["jel-labels-en"] + " " + ' '.join(publi["jel-labels-en"])
	if "jel-labels-fr" in publi:
		upd_author["jel-labels-fr"] = old_author["jel-labels-fr"] + " " + ' '.join(publi["jel-labels-fr"])
		for jel_label in publi["jel-labels-fr"]:
			AUTHOR_SPECIALTIES[name_hash][jel_label] += 1
		upd_author["show_specialites"] = specialties_label(AUTHOR_SPECIALTIES[name_hash])
	if "keywords" in publi:
		upd_author["keywords"] = list(set(old_author["keywords"]) | set(publi["keywords"]))
	if "title" in publi:
		upd_author["titles"] = old_author["titles"] +  " " + publi["title"]
	upd_author["pub_ids"] = sorted(old_author["pub_ids"] + [pub_tuple], key=valid_pubdate, reverse=True)
	# TODO see if abstracts can fit in
	resp = ES.update(index=ES_INDEX_AUTHOR, id=aid, body={ "doc": upd_author })

'''
	Indexing method used for a publication author who is not yet in the authors index.

	In this case, mainly the  publication list is updated.
'''
def index_new_author(publi, pub_tuple, pub_date, author, aid_by_hash, full_name, name_hash):
	obj = {
		"full_name": full_name,
		"aliases": [full_name],
		"institutions": author["institution"] if "institution" in author else "",
		"jel-labels-en": ' '.join(publi["jel-labels-en"]) if "jel-labels-en" in publi else "",
		"jel-labels-fr": ' '.join(publi["jel-labels-fr"]) if "jel-labels-fr" in publi else "",
		"keywords": publi["keywords"] if "keywords" in publi else [],
		"titles": publi["title"] if "title" in publi else "",
		"pub_ids": [pub_tuple]
		# TODO see if they fit "abstracts": publi["abstracts"]
	}
	if "institution" in author:
		inst = author["institution"]
		obj["current_institution"] = inst 
		fetch_logo(inst, obj)
	if pub_date:
		obj["latest_pub_date"] = pub_date
	if name_hash in TOP_AUTHORS:
		home_url = TOP_AUTHORS[name_hash]
		if len(home_url) > 0:
			obj["home_url"] = home_url
		if CRAWL_IMAGES:
			img_urls = list(image_crawl.yield_image_urls([full_name]))
			logging.debug("Found {} pictures for author {}".format(len(img_urls), full_name))
			if len(img_urls) > 0:
				obj["pic_urls"] = img_urls
	if "jel-labels-fr" in publi:
		for jel_label in publi["jel-labels-fr"]:
			AUTHOR_SPECIALTIES[name_hash][jel_label] += 1
	obj["show_specialites"] = specialties_label(AUTHOR_SPECIALTIES[name_hash])
	resp = ES.index(index=ES_INDEX_AUTHOR, body=obj)
	aid_by_hash[name_hash] = resp["_id"]
	logging.debug("Saved new author: {} --> {}".format(full_name, name_hash))

MAX_DISPLAYED_SPECIALTIES = 3
def specialties_label(specs):
	if len(specs) < MAX_DISPLAYED_SPECIALTIES:
		return "; ".join(specs.keys())
	else:
		return "; ".join([k for k, v in specs.most_common(MAX_DISPLAYED_SPECIALTIES)]) 
		+ " (et {} autres)".format(len(specs) - MAX_DISPLAYED_SPECIALTIES)

def index_authors_from_publis():
	aid_by_hash = { }
	resp = scan(ES, scroll='360m', index=ES_INDEX_PUBLI, query={ "query": { "match_all": {} } })
	for hit in resp:
		publi = hit["_source"]
		pub_id = hit["_id"]
		pub_date = publi["creation-date"] if "creation-date" in publi else None
		pub_tuple = { "pub_id": pub_id, "pub_date": pub_date }
		for author in publi["authors"]:
			full_name = author["full_name"]
			name_hash = hash_name(full_name)
			if not name_hash:
				logging.error("Could not compute name hash for {} (while indexing {})".format(full_name, publi))
			elif name_hash in aid_by_hash:
				index_existing_author(publi, pub_tuple, author, aid_by_hash, full_name, name_hash)
			else:
				index_new_author(publi, pub_tuple, pub_date, author, aid_by_hash, full_name, name_hash)
	ES.indices.refresh(index=ES_INDEX_AUTHOR)

if __name__ == "__main__":
	try:
		ES.indices.delete(index=ES_INDEX_AUTHOR)
		print("Re-creating index", ES_INDEX_AUTHOR)
	except:
		print("Creating index", ES_INDEX_AUTHOR)
	ES.indices.create(index=ES_INDEX_AUTHOR, body=MAPPING_AUTHOR)
	index_authors_from_publis()
