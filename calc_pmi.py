import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
import math
data = pd.read_csv('./data/dataset.csv')
import csv
# print(word_tokenize(data['review_texts'][1]))
total_freq = {}
pos_freq = {}
neg_freq = {}
pos_length = 0
neg_length = 0
for e in data['ratings_binary']:
    if e == 'p':
        pos_length += 1
    else:
        neg_length += 1
# pos_length = filter(lambda e : e == 'p', [e for e in  data['ratings_binary']] ))
# neg_length = len(filter(lambda e : e == 'n', [e for e in  data['ratings_binary']] ))
# print(data)
for index, e in data.iterrows():

    review = str(e['review_texts']).lower()
    tokens = word_tokenize(review)
    for i in tokens:
        total_freq[i] = 0 if i not in total_freq else total_freq[i] + 1
    if e['ratings_binary'] == 'p':
        pos_freq[i] = 0 if i not in pos_freq else pos_freq[i] + 1
    if e['ratings_binary'] == 'n':
        neg_freq[i] = 0 if i not in neg_freq else neg_freq[i] + 1
    



sentiment_score = {}
for key,value in total_freq.items():
    if (value < 10): continue
    freq_w_p = 0 if key not in pos_freq else pos_freq[key] 
    freq_w_n = 0 if key not in neg_freq else neg_freq[key] 
    sentiment_score[key] = math.log2(((freq_w_p+1) * neg_length ) / ((freq_w_n + 1) * pos_length))

with open("./sentiment_score.csv", "w") as file:
    writer = csv.writer(file)
    for key, value in sentiment_score.items():
        writer.writerow([key, value])
    file.close()