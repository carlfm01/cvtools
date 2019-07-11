#!/usr/bin/python

import sys, getopt, re
from collections import defaultdict
import spacy

input_file = ''
dictionary_file = ''
limit = 0
min_frequency = 0
max_frequency = 0
words_only = 0

try:
	opts, args = getopt.getopt(sys.argv[1:],"i:d",["input=","dictionary=","limit=","min-frequency=","max-frequency=","show-words-only"])
except getopt.GetoptError:
	print('word_usage.py -i <input file> [-d <dictionary>] [--limit x] [--min-frequency x] [--max-frequency x] [--show-words-only]')
	sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		print('word_usage.py -i <input file> [-d <dictionary>] [--limit x] [--min-frequency x] [--max-frequency x] [--show-words-only]')
		sys.exit()
	elif opt in ("-i", "--input"):
		input_file = arg
	elif opt in ("-d", "--dictionary"):
		dictionary_file = arg
	elif opt == "--limit":
		limit = int(arg)
	elif opt == "--min-frequency":
		min_frequency = int(arg)
	elif opt == "--max-frequency":
		max_frequency = int(arg)
	elif opt == "--show-words-only":
		words_only = 1

word_dict = defaultdict(int)

# Scan sentences
with open(input_file, encoding='UTF-8') as f:  
	for line in f:
		# Convert curly apostrophes to straight
		line = line.replace(u"\u2018","'")
		line = line.replace(u"\u2019","'")
		line = line.replace(u"\u0060","'")
		line = line.replace(u"\u00b4","'")
	
		words = line.lower().split()
		
		for w in words:
			# Filter out symbols
			w = re.sub('[^a-zA-Z\u00c0-\u024f\u1e00-\u1eff\']', '', w)
		
			# Ignore apostrophes at start or end
			if len(w) > 1 and w[:1] == "'":
				w = w[1:]
				
			if len(w) > 1 and w[-1] == "'":
				w = w[:-1]
		
			if len(w) > 0:
				val = word_dict[w]
				val += 1
				word_dict[w] = val

# Scan dictionary if the user specified it (assumes one word per line)
if min_frequency == 0 and dictionary_file:
	with open(dictionary_file) as f:  
		for line in f:
			line = line.lower()
			
			# Convert curly apostrophes to straight
			line = line.replace(u"\u2018","'")
			line = line.replace(u"\u2019","'")
			line = line.replace(u"\u0060","'")
			line = line.replace(u"\u00b4","'")

			# Filter out symbols
			line = re.sub('[^a-zA-Z\u00c0-\u024f\u1e00-\u1eff\']', '', line)
		
			if len(line) > 0:
				# Add word if it doesn't exist
				val = word_dict[line]
				word_dict[line] = val

# Filter by min/max frequency
filtered_words = defaultdict(int)

for word in word_dict:
	if (min_frequency == 0 or int(word_dict[word]) >= min_frequency) and \
	(max_frequency == 0 or int(word_dict[word]) <= max_frequency):
		filtered_words[word] = word_dict[word]		

# Now sort by alphabetical order of word
sorted_words = sorted(filtered_words.items(), key=lambda x:x[0]);

# Sort words by most to least frequent
sorted_words = sorted(sorted_words, key=lambda x:x[1], reverse=True);

# Set limit if specified
if limit > 0 and len(sorted_words) > limit:
	sorted_words = sorted_words[:limit]

spacy_nlp = spacy.load('es_core_news_md')

with open('sentences-result.txt', 'a', encoding='UTF-8') as output_file:
    for idx, doc in enumerate(spacy_nlp.pipe([item[0] for item in sorted_words], batch_size=700)):
        output_file.write('{0} {1} {2}\n'.format(
            doc[0].text.replace('\n', ''), sorted_words[idx][1], doc[0].is_oov))


for word, num in sorted_words:
    if words_only:
        print(word)
    else:
        result = "{} {}".format(word, num)
        print(result)
