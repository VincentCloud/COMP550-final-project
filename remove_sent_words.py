from nltk import text
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize

data = pd.read_csv('./data/dataset.csv')
# print(data)
def text2list(filename):
    res = []
    with open(filename, 'r') as fd:
        lines = fd.readlines()
        for line in lines:
            res.append(line.strip())
    return res 
# neg_words =  text2list('data/opinion-lexicon-English/negative-words.txt')
# pos_words =  text2list('data/opinion-lexicon-English/positive-words.txt')
# sent_words = set((text2list('data/sentiment_words.txt')))
# # print(neg_words)
# pos_words += (neg_words)
# words = []
# for i in pos_words:
#     if i in sent_words: words.append(i)

words = text2list('data/sentiment_words.txt')

def in_forbidden_word(word):
    for i in words:
        if i in word:
            return True
    return False

# print(word_tokenize(data['review_texts'][1]))
def replace(review):
    try:
        review = str(review).lower()
        tokens = word_tokenize(review)
        tokens = ['_UNKNOWN_' if in_forbidden_word(token) else token for token in tokens ]
        replaced_review = ' '.join(tokens).strip()
        return replaced_review
    except:
        return 'NC'


data['review_texts'] = [replace(e) for e in data['review_texts']]
data.to_csv('./data/dataset_without_sent_all.csv', index=False)

