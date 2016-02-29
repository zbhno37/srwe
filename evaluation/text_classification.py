import sys
sys.path.append('../src')
from utils import load_w2v_model
from collections import defaultdict
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
english_stopwords = stopwords.words('english')
english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
words_to_remove = english_stopwords + english_punctuations

def clean_text(text):
    return [word.lower() for word in word_tokenize(text) if word not in words_to_remove]

def get_vec_from_words(words, model, d):
    vec_sum = np.zeros(d)
    for word in words:
        if word in model:
            vec_sum += model[word]
    return vec_sum

def get_vec_len(model):
    vec_len = 0
    for each in model:
        vec_len = len(model[each])
        break
    return vec_len

def load_nytimes(filename, model):
    d = get_vec_len(model)
    corpus_vec = []
    corpus_label = []
    line_count = 0
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split('\t')
            corpus_vec.append(get_vec_from_words(clean_text(arr[0].decode('utf-8')), model, d))
            corpus_label.append(arr[1])
            if line_count % 1000 == 0:
                logging.info('loading nytimes... %d' % line_count)
            line_count += 1
    return np.array(corpus_vec), corpus_label

def transfer_label(labels, target):
    res = [1 if x == target else 0 for x in labels]
    return np.array(res)

def train(label, X_train, X_test, y_train, y_test):
    logging.info('training %s' % label)
    y_train_label = transfer_label(y_train, label)
    y_test_label = transfer_label(y_test, label)
    clf = LogisticRegression()
    clf.fit(X_train, y_train_label)
    acc = clf.score(X_test, y_test_label)
    logging.info('%s acc:%lf' % (label, acc))

def main():
    model_file = '../../paper/data/srwe_model/wiki_small.w2v.model'
    nytimes_file = '../gen_data/nytimes/news_corpus'
    model = load_w2v_model(model_file, logging, nparray=True)
    corpus_vec, corpus_label = load_nytimes(nytimes_file, model)
    labels = list(set(corpus_label))
    X_train, X_test, y_train, y_test = train_test_split(corpus_vec, corpus_label, test_size=0.2, random_state=42)
    logging.info('train size: %d, test size:%d' % (len(y_train), len(y_test)))
    for label in labels:
        train(label, X_train, X_test, y_train, y_test)

if __name__ == '__main__':
    main()

