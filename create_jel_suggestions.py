import index_publis

print("SUGGESTIONS_JEL = [")
for _, label in index_publis.JEL_CODEMAP.items():
	print('"{}",'.format(label))
print("]")
