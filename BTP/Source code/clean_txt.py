 # -*- coding: utf-8 -*- 

import re, json
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import pandas as pd

def spellCheck(text):
	wiki = TextBlob(text)
	return wiki.correct()

def preprocess(txt, lemmatizer):
	txt = txt.lower()
	txt = txt.replace("-", " ")
	txt = txt.replace("_", " ")
	txt = txt.replace("(", " ")
	txt = txt.replace(")", " ")
	txt = txt.replace("/", "")

	with open('words.json') as json_data:
		word_dic = json.load(json_data)

	pattern = re.compile(r'\b(' + '|'.join(word_dic.keys()) + r')\b')
	review = pattern.sub(lambda x: word_dic[x.group()], txt)

	# review = spellCheck(review)
	# return review
	words = review.split()
	tmp = [lemmatizer.lemmatize(word, pos="v") for word in words]

	return ' '.join(tmp)


if __name__=="__main__":
	pos_df = pd.read_csv('pos.txt')
	neg_df = pd.read_csv('neg.txt')
	lemmatizer = WordNetLemmatizer()
	pos_li = []
	neg_li = []
	for x in range(len(pos_df['text'])):
		pos_li.append(preprocess(pos_df['text'][x], lemmatizer))

	print "done till here"

	for x in range(len(neg_df['text'])):
		neg_li.append(preprocess(neg_df['text'][x], lemmatizer))

	negfile = open('cleaned_neg.text', 'w')
	for txt in neg_li:
		negfile.write("%s\n"%txt)

	posfile = open('cleaned_pos.text', 'w')
	for txt in pos_li:
		posfile.write("%s\n"%txt)

	