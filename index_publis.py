#!/usr/bin/python3
import re, io, glob, sys, logging
from datetime import datetime
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

logging.basicConfig(level=logging.WARNING)

# Safety flag
RECREATE_INDEX = True

ES_PORT = 9200

ES_INDEX_PUBLI = 'publication'

'''
	ES mapping used for the publication index.

	Includes the synonym list used to handle acronymized variants of institution names.
'''	
MAPPING_PUBLI = {
	"settings": {
		"number_of_shards": 1
	},
    "mappings": {
        "properties": {
        	# Publication title
            "title": { "type": "text" },
        	# Publication abstract
            "abstract": { "type": "text" },
            # JEL topic (in English, not the JEL code)
            "jel-labels-en": { "type": "text" },
            # JEL topic (in French, not the JEL code)
            "jel-labels-fr": { "type": "text" },
            # Keywords as a separate field
            "keywords": { "type": "text" },
            # Publication date
            "creation_date": { "type": "text" },
            # List of authors
            "authors":  { 
            	"type": "nested", 
          		"properties": {
          			"full_name": { "type": "text" },
          			"first_name": { "type": "text" },
          			"last_name": { "type": "text" },
          			# Affiliation at the time of this publication
          			"institution": { "type": "text" }
          		}
			}
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

JEL_CODEMAP_EN = { }
JEL_CODEMAP_FR = { }
for l in lines("./jel_map"):
	cl = list([i.strip() for i in l.split("|")])
	code = cl[1]
	label_en = cl[0].replace("Other", "").replace("General", "").replace(":", "")
	JEL_CODEMAP_EN[code] = label_en
	label_fr = cl[2].replace("Autre", "").replace("Général", "").replace(":", "")
	JEL_CODEMAP_FR[code] = label_fr

# RE_FIELD_VALUE = re.compile(r"([\w\-]+): (.+)")
RE_FIELD_VALUE = re.compile(r"([^: ]+): ?(.+)")

# RE_DATE_VALUE = re.compile(r"((20[012][0-9])|(19[0-9]{2}))(\-((0?[1-9])|1[0-2])(\-[0-3][0-9])?)?$")
RE_DATE_VALUE = re.compile(r"((20[012][0-9])|(19[0-9]{2}))(\-((0[1-9])|1[0-2])(\-[0-3][0-9])?)?$")

AUTHOR_FIELDS = {
	"Author-Name-First".lower(): 'first_name',
	"Author-Name-Last".lower(): 'last_name',
	"Author-Email".lower(): 'email',
	"Author-Workplace-Name".lower(): 'institution'
}

INST_COUNTER = Counter()

def is_accepted_tpl(val):
	return val in ["ReDIF-Article 1.0", "ReDIF-Paper 1.0"]
	# return True

def jel_labels_en(val):
	for c in re.split(r';|,| ', val):
		code = c.strip()
		if not code:
			continue
		try:
			yield JEL_CODEMAP_EN[code]
		except KeyError:
			if len(code) == 2:
				try:
					yield JEL_CODEMAP_EN[code + "0"]
				except KeyError:
					logging.error("JEL code not found ({} nor {})".format(code, code + "0"))	

def jel_labels_fr(val):
	for c in re.split(r';|,| ', val):
		code = c.strip()
		if not code:
			continue
		try:
			yield JEL_CODEMAP_FR[code]
		except KeyError:
			if len(code) == 2:
				try:
					yield JEL_CODEMAP_FR[code + "0"]
				except KeyError:
					logging.error("JEL code not found ({} nor {})".format(code, code + "0"))	

def keywords(val):
	for k in re.split(r';|,', val):
		keyword = k.strip()
		if not keyword:
			continue
		yield keyword

def parse_date(val):
	for f in ['%Y-%m-%d', '%Y-%m', '%Y', '%Y/%m/%d', '%Y/%m', '%m/%d/%Y', '%Y%m%d', '%Y%m']:
		try:
			return datetime.strptime(val, f)
		except ValueError as ve:
			pass
	return None

def parse_repec_file(f):
	tpl = None
	obj = None
	grp, key, txt = None, None, []
	for l in lines(f):
		m = RE_FIELD_VALUE.match(l)
		if m:
			if len(txt) > 0:
				if key and obj:
					obj[key] = '\n'.join(txt)
				key, txt = None, []
			key, val = m.group(1).lower(), m.group(2).strip()
			if len(val) < 1:
				continue
			if key in AUTHOR_FIELDS:
				if grp:
					grp[AUTHOR_FIELDS[key]] = val
			elif key == "Author-Name".lower():
				if grp and obj:
					obj["authors"].append(grp)
				grp = { "full_name": val }
			else:
				if key.endswith("Template-Type".lower()):
					if obj is not None: 
						if grp:
							obj["authors"].append(grp)
						yield obj
						obj = None
					if is_accepted_tpl(val):
						obj = { "type" :  val, "authors": [] }
					grp = None
				elif key in ["Title".lower(), "Abstract".lower()]:
					txt = [val]
				elif obj and key == "Creation-Date".lower():
					date = parse_date(val)
					if date:
						obj["creation-date"] = date
					else:
						logging.warning("Invalid creation date: {}".format(val))
				elif obj and key == "File-URL".lower():
					obj["url"] = val
				elif obj and key == "Classification-JEL".lower():
					obj["jel-labels-en"] = list(jel_labels_en(val))
					obj["jel-labels-fr"] = list(jel_labels_fr(val))
				elif obj and key == "Keywords".lower():
					obj["keywords"] = list(keywords(val))
		elif txt and len(l) > 0:
			txt.append(l)
	if obj is not None: 
		if grp:
			obj["authors"].append(grp)
		yield obj

def yield_bulk_items(d):
	for f in glob.glob("{}/**/*.rdf".format(d)):
		logging.debug("Processing file", f)
		for obj in parse_repec_file(f):
			obj["_index"] = ES_INDEX_PUBLI
			for author in obj["authors"]:
				if "institution" in author:
					INST_COUNTER[author["institution"]] += 1
			yield obj

def parse_repec_root_bulk(p):
	path = Path(p)
	for f in path.iterdir():
		if f.is_dir():
			print("Processing directory", f)
			for success, info in parallel_bulk(ES, yield_bulk_items(f)):
				if not success:
					logging.error('Failed to index a publication', info)

COMPUTE_TOP_INSTITUTIONS = False

if __name__ == "__main__":
	if RECREATE_INDEX:
		try:
			ES.indices.delete(index=ES_INDEX_PUBLI)
			print("Re-creating index", ES_INDEX_PUBLI)
		except:
			print("Creating index", ES_INDEX_PUBLI)
		ES.indices.create(index=ES_INDEX_PUBLI, body=MAPPING_PUBLI)
	parse_repec_root_bulk("./repec_data/data/")
	if COMPUTE_TOP_INSTITUTIONS:
		print("Most popular institutions")
		for k, v in INST_COUNTER.most_common(10000):
			print(k)
