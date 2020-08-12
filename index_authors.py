#!/usr/bin/python3
import re, io, glob, logging, sys
from pathlib import Path
from multiprocessing import Pool
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk, scan
from collections import Counter

# Position this flag to False if you wish to build a quick index, without images (author pictures and institution logos)
CRAWL_IMAGES = True

logging.basicConfig(level=logging.WARNING)

ES_PORT = 9200
ES_INDEX_PUBLI = 'publication'

ES_INDEX_AUTHOR = 'author'
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
            # List of institutions (appear n times if n publications signed by this author when affiliated to that institution)
			"institutions": { "type": "text" },
			# List of topics (in English, not the JEL codes!), appear n times if n papers published by this author on that JEL topic 
			"specialties": { "type": "text" },
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

BROWSER = None
if CRAWL_IMAGES:
	import image_crawl
	BROWSER = image_crawl.create_browser()
	TOP_AUTHORS = set(lines('top_authors.uniq'))
	logging.warning("Loaded {} top authors".format(len(TOP_AUTHORS)))
	TOP_INSTITS = set(lines("top_institutions"))
	logging.warning("Loaded {} top institutions".format(len(TOP_INSTITS)))

INST_LOGOS = dict()

def valid_pubdate(t):
	return t["pub_date"] if "pub_date" in t and t["pub_date"] else "2020-08"

# def name_pivot(full_name):
# 	l = list([i.strip() for i in full_name.split(",")])
# 	if len(l) > 1:
# 		return " ".join(l)
# 	l = list([i.strip() for i in re.split(r'\.| ', full_name) if len(i.strip()) > 1])
# 	if len(l) > 0:
# 		return " ".join(l)
# 	return None

def remove_comma(n):
	l = list([i.strip() for i in n.split(",")])
	if len(l) < 2:
		return n
	if len(l) > 2:
		logging.error("Found full name with several commas: {}".format(n))
	return l[1] + " " + l[0]	

def hash_name(n):
	m = remove_comma(n)
	l = list([i.lower().strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 0])
	if len(l) > 0:
		for i in range(1, len(l)-1):
			l[i] = l[i][0]
		return " ".join(l)
	return None

'''
Picks the best variant among several full names for the same person.
The best variant first maximizes the token count, then maximizes the number of full tokens (as opposed to initials), finally minimizes the number of commas.
For example with "Harvey, Andrew C.", "Andrew C. Harvey", "Andrew Harvey", "Andrew Charles Harvey", the latter will be selected.
'''
def best_name_variant(names):
	best = sorted(names, key=name_variant_key, reverse=True)[0]
	return " ".join([i[0].upper() + (i[1:].lower() if len(i) > 1 else "") for i in best.split(" ") if len(i) > 0])

def name_variant_key(n):
	return metric_token_count(n), metric_full_token_count(n), metric_comma_count(n)

# 1st metric to select the best name variant
def metric_token_count(n):
	m = remove_comma(n)
	l = list([i.strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 0])
	return len(l)

# 2nd metric to select the best name variant
def metric_full_token_count(n):
	m = remove_comma(n)
	l = list([i.strip(". ") for i in re.split(r'\.| ', m) if len(i.strip(". ")) > 1])
	return len(l)

# 2nd metric to select the best name variant
def metric_comma_count(n):
	return 0 if n.count(",") > 0 else 1

def index_authors_from_publis():
	aid_by_hash = { }
	resp = scan(ES, index=ES_INDEX_PUBLI, query={ "query": { "match_all": {} } })
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
				continue
			if name_hash  in aid_by_hash:
				logging.debug("Already existing author: {} --> {}".format(full_name, name_hash))
				aid = aid_by_hash[name_hash]
				obj = ES.get(index=ES_INDEX_AUTHOR, id=aid)
				upd_author = { }
				old_author = obj["_source"]
				if full_name not in old_author["aliases"]:
					upd_author["aliases"] = old_author["aliases"] + [full_name]
					upd_author["best_name"] = best_name_variant(upd_author["aliases"])
					logging.warning("Picked best variant {} among {}".format(upd_author["best_name"], upd_author["aliases"]))
				if "institution" in author:
					inst = author["institution"]
					upd_author["institutions"] = inst + " " + old_author["institutions"]
					if "creation-date" in publi:
						if "latest_pub_date" not in old_author or old_author["latest_pub_date"] < publi["creation-date"]:
							upd_author["current_institution"] = inst
							upd_author["latest_pub_date"] = publi["creation-date"]
							if CRAWL_IMAGES and inst in TOP_INSTITS:
								if inst not in INST_LOGOS:
									query_str = ' '.join(inst.split("-")[:2])
									logo_urls = list(image_crawl.yield_image_urls(BROWSER, ["logo", query_str]))
									logging.info("Found {} logos of {}".format(len(logo_urls), query_str))
									INST_LOGOS[inst] = logo_urls
								else:
									logo_urls = INST_LOGOS[inst]
								if len(logo_urls) > 0:
									upd_author["logo_urls"] = logo_urls
				if "jel-labels" in publi:
					upd_author["jel-labels"] = old_author["jel-labels"] + " " + ' '.join(publi["jel-labels"])
					upd_author["specialties"] = list(set(old_author["specialties"]) | set(publi["jel-labels"]))
				if "keywords" in publi:
					upd_author["keywords"] = list(set(old_author["keywords"]) | set(publi["keywords"]))
				if "title" in publi:
					upd_author["titles"] = old_author["titles"] +  " " + publi["title"]
				upd_author["pub_ids"] = sorted(old_author["pub_ids"] + [pub_tuple], key=valid_pubdate, reverse=True)
				# TODO see if abstracts can fit in
				resp = ES.update(index=ES_INDEX_AUTHOR, id=aid, body={ "doc": upd_author })
			else:
				obj = {
					"full_name": full_name,
					"aliases": [full_name],
					"institutions": author["institution"] if "institution" in author else "",
					"jel-labels": ' '.join(publi["jel-labels"]) if "jel-labels" in publi else "",
					"specialties": publi["jel-labels"] if "jel-labels" in publi else [],
					"keywords": publi["keywords"] if "keywords" in publi else [],
					"titles": publi["title"] if "title" in publi else "",
					"pub_ids": [pub_tuple]
					# TODO see if they fit "abstracts": publi["abstracts"]
				}
				if "institution" in author:
					inst = author["institution"]
					obj["current_institution"] = inst 
					if CRAWL_IMAGES and inst in TOP_INSTITS:
						if inst not in INST_LOGOS:
							logo_urls = list(image_crawl.yield_image_urls(BROWSER, ["logo", inst]))
							logging.info("Found {} logos of {}".format(len(logo_urls), inst))
							INST_LOGOS[inst] = logo_urls
						else:
							logo_urls = INST_LOGOS[inst]
						if len(logo_urls) > 0:
							obj["logo_urls"] = logo_urls
				if pub_date:
					obj["latest_pub_date"] = pub_date
				if CRAWL_IMAGES and full_name in TOP_AUTHORS:
					img_urls = list(image_crawl.yield_image_urls(BROWSER, [full_name]))
					logging.info("Found {} pictures of {}".format(len(img_urls), full_name))
					if len(img_urls) > 0:
						obj["pic_urls"] = img_urls
				resp = ES.index(index=ES_INDEX_AUTHOR, body=obj)
				aid_by_hash[name_hash] = resp["_id"]
				logging.debug("Saved new author: {} --> {}".format(full_name, name_hash))
	ES.indices.refresh(index=ES_INDEX_AUTHOR)

if __name__ == "__main__":
	try:
		ES.indices.delete(index=ES_INDEX_AUTHOR)
		print("Re-creating index", ES_INDEX_AUTHOR)
	except:
		print("Creating index", ES_INDEX_AUTHOR)
	ES.indices.create(index=ES_INDEX_AUTHOR, body=MAPPING_AUTHOR)
	try:
		index_authors_from_publis()
	finally:
		if CRAWL_IMAGES:
			image_crawl.destroy_browser(BROWSER)

