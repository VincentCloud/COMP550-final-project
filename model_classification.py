# -*- coding: utf-8 -*-
"""

@author: shuhao
"""
import nltk

from nltk.corpus import wordnet
from collections import Counter
import pandas as pd
import numpy as np

from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer

from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk import RegexpTokenizer,word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re

samelength = False # If true, make critic and audience dataframe same length by dropping some critic data

tokenizor_decision ="RegexpTokenizer"   #choose between RegexpTokenizer and word_tokenize
preprocess_decision = ["","","","lemmatizer"] #choose from "stopwords","porter_stemmer","snowball_stemmer","lemmatizer"
feature_extraction_decision = "TfidfVectorizer"    #choose between CountVectorizer and TfidfVectorizer




"""
    Read data from files
"""
def getData():

    df = pd.read_csv('./data/dataset.csv')
    #remove the nan value
    df = df.dropna()
    
    c_df = df.loc[df['sources'] == 'critics']
    a_df = df.loc[df['sources'] == 'audience']

    if samelength:
        #make two dataframe same length
        c_df = c_df.iloc[:len(a_df)]

    return c_df,a_df,df

"""
    Data preprocessing
"""

def preprocessing(line):
     
     processed_line = line
    
     if tokenizor_decision =="word_tokenize":
         processed_line=word_tokenize(processed_line)
    
     if tokenizor_decision =="RegexpTokenizer":
         tokenizer = RegexpTokenizer(r'\w+')
         processed_line=tokenizer.tokenize(processed_line)
    
     
     if "snowball_stemmer" in preprocess_decision:
         stemmer=SnowballStemmer('english')
         processed_line=[stemmer.stem(word) for word in processed_line]
         
     if "porter_stemmer" in preprocess_decision:
        stemmer=PorterStemmer()
        processed_line=[stemmer.stem(word) for word in processed_line]
        
     if "stopwords" in preprocess_decision:
        stop_words = stopwords.words('english')
        processed_line= [word for word in processed_line if  word not in stop_words]
        
     if "lemmatizer" in preprocess_decision:
        lemmatizer=WordNetLemmatizer()
        processed_line=[lemmatizer.lemmatize(word) for word in processed_line]
 
    
     return processed_line

"""
Data split and feature extraction
"""


def feature_extraction(X,Y):
    x_train, x_val,y_train,y_val = model_selection.train_test_split(X,Y,test_size=0.2,random_state=10)
    x_val, x_test, y_val, y_test = model_selection.train_test_split(x_val,y_val,test_size=0.5,random_state=10)
    
    
    if feature_extraction_decision == "CountVectorizer":
        vect =CountVectorizer(min_df=2)
        
    if feature_extraction_decision == "TfidfVectorizer":
        vect =TfidfVectorizer(min_df=2)
        
    vect.fit(x_train)
    x_train_vect = vect.transform(x_train)
    x_val_vect=vect.transform(x_val)
    x_test_vect=vect.transform(x_test)
    
    return  x_train_vect, x_val_vect,x_test_vect,y_train,y_val,y_test



def get_prediction(data):
    X = []
    Y = []
    tag=[]
    word_size = 0
    review = data['review_texts'].tolist()
    rating = data['ratings_binary'].tolist();
    
    #data preprocessing
    
    for line in review:
    
        processed_line=preprocessing(line)
        processed_line=[re.sub('[0-9+]','',word) for word in processed_line]
        processed_line=' '.join(processed_line)
        X.append(processed_line)
    
    
    Y = rating
    print("  size of features: ",len(X))
    print("  size of labels: ",len(Y))

        
    for sentence in X:
        word_size+=len(word_tokenize(sentence))
        
        tag+=( [i for i in pos_tag(word_tokenize(sentence),tagset='universal')])

    
    count= Counter([j for i,j in tag])
    count_dict = count.items()
    count_dict = {k : v/word_size for k,v in count_dict}
    new_count_dict  = dict((k, count_dict[k]) for k in ['NOUN', 'VERB','ADJ','ADV'] if k in count_dict)
    print("  Percentage of each pos tag: ",new_count_dict)
    
    #feature extraction
    x_train_vect,x_val_vect,x_test_vect,y_train,y_val,y_test = feature_extraction(X,Y)
    
    
    #feed data into model
    LR =LogisticRegression(C=1.2,random_state=0, solver='lbfgs',multi_class='multinomial',max_iter=300)
    LR.fit(x_train_vect, y_train)
    accuracy=LR.score(x_val_vect,y_val)
    print("  accuracy=", accuracy)


#read data
critics_data, audience_data, general_data= getData()


print("critics result:")
get_prediction(critics_data)

print("audience result:")
get_prediction(audience_data)

print("general result:")
get_prediction(general_data)
