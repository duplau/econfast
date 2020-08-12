#!/usr/bin/python3
import re, io, glob, sys, logging, unicodedata
from datetime import datetime
from pathlib import Path
from multiprocessing import Pool
from functools import reduce

logging.basicConfig(level=logging.WARNING)

ENCODINGS = ['utf-8', 'utf-16-le']

MAX_ITEMS = 10000

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

def stripped(s): return s.strip(" -_.,'?!").strip('"').strip()

def lower_or_not(token):
	return token.lower()

def to_ASCII(phrase): return unicodedata.normalize('NFKD', phrase)

def replace_by_space(str, *patterns): return reduce(lambda s, p: re.sub(p, ' ', s), patterns, str)

def case_token(t): return to_ASCII(lower_or_not(t.strip()))

def pre_split(v):
	s = ' ' + v.strip() + ' '
	s = replace_by_space(s, '[\{\}\[\](),\.\"\';:!?&\^\/\*-]')
	return re.sub('([^\d\'])-([^\d])', '\1 \2', s)

def is_valid_token(token):
	token = stripped(token)
	if len(token) < 2: return False
	if token.isspace() or not token: return False
	if token.isdigit(): return False
	if len(token) <= 2 and not (token.isalpha() and token.isupper()): return False
	return True

def is_valid_phrase(tokens): return len(tokens) > 0 and not all(len(t) < 2 or t.isdigit() for t in tokens)

def normalize_and_validate_tokens(phrase):
	if phrase:
		tokens = map(lambda t: case_token(t), str.split(pre_split(phrase)))
		validTokens = []
		for token in tokens:
			if is_valid_token(token): validTokens.append(token)
		if is_valid_phrase(validTokens): return validTokens
	return []

def normalize_and_validate_phrase(value):
	tokens = normalize_and_validate_tokens(value)
	return ' '.join(tokens) if len(tokens) > 0 else None

RE_FIELD_VALUE = re.compile(r"([^: ]+): ?(.+)")

YIELD_COMPOUNDS = False

def fetch_name(res):
	if res[0]:
		if res[1]:
			# yield res[1]
			if YIELD_COMPOUNDS:
				yield res[0] + " // " + res[1]
		yield res[0]
		# else:
		# 	yield res[0]

def yield_some(res, res_en):
	if ENGLISH_ONLY:
		if res_en[0]:
			for i in fetch_name(res_en): yield i
		else:
			for i in fetch_name(res): yield i
	else:
		for i in fetch_name(res): yield i
		for i in fetch_name(res_en): yield i

def yield_institutions(f):
	key = None
	res, res_en = [None]*2, [None]*2
	for l in lines(f):
		m = RE_FIELD_VALUE.match(l)
		if m:
			key, val = m.group(1).lower(), m.group(2).strip().replace('"', "'")
			if len(val) < 1:
				continue
			if key == "primary-name":
				for i in yield_some(res, res_en): yield i
				res, res_en = [None]*2, [None]*2
			if key == "primary-name":
				res[0] = val
			if key == "secondary-name":
				res[1] = val
			if key == "primary-name-english":
				res_en[0] = val
			if key == "secondary-name-english":
				res_en[1] = val
	for i in yield_some(res, res_en): yield i

def yield_synonyms(f):
	return

def print_all_institutions(p):
	count = 0
	path = Path(p)
	for f in glob.glob("{}/*.rdf".format(p)):
		for i in yield_institutions(f) if MODE == MODE_AUTOSUGGEST else yield_synonyms(f):
			count += 1
			print(i)
			if count >= MAX_ITEMS:
				return

MODE_SYNONYMS = 1 # To produce a list of synonyms in Solr format (with english conversion, "1 2"->"2" simplification)
MODE_AUTOSUGGEST = 2 # To produce the list of auto-completions (for institutions - there will be another list for JEL topics)

MODE = MODE_SYNONYMS
ENGLISH_ONLY = True
if __name__ == "__main__":
	print_all_institutions("./repec_data/data/edi/inst")
