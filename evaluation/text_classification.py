import sys
sys.path.append('../src')
from utils import load_w2v_model
from collections import defaultdict
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
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
            if line_count % 50000 == 0:
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
    ans = clf.predict_proba(X_test[0].reshape(1, -1))
    #print clf.classes_
    #print type(ans)
    #print ans
    return clf
    #acc = clf.score(X_test, y_test_label)
    #logging.info('%s acc:%lf' % (label, acc))
    #y_pred = clf.predict(X_test)
    #precision, recall, f_score, support = precision_recall_fscore_support(y_test_label, y_pred, average='binary')
    #logging.info('%s,length:%d,precision:%.4lf,recall:%.4lf,f_score:%.4lf' % (label, y_test_label.shape[0], precision, recall, f_score))

def main():
    model_file = '../../paper/data/srwe_model/wiki_small.w2v.model'
    nytimes_file = '../gen_data/nytimes/news_corpus'
    model = load_w2v_model(model_file, logging, nparray=True)
    corpus_vec, corpus_label = load_nytimes(nytimes_file, model)
    labels = list(set(corpus_label))
    X_train, X_test, y_train, y_test = train_test_split(corpus_vec, corpus_label, test_size=0.2, random_state=42)
    logging.info('train size: %d, test size:%d' % (len(y_train), len(y_test)))
    clfs = {}
    for label in labels:
        clfs[label] = train(label, X_train, X_test, y_train, y_test)

    y_pred = []
    for each in X_test:
        pred_res = []
        for label in clfs:
            pred_res.append((clfs[label].predict_proba(each.reshape(1, -1))[0][1], label))
        sorted_pred = sorted(pred_res, key=lambda x: x[0], reverse=True)
        y_pred.append(sorted_pred[0][1])
    precision, recall, f_score, support, present_labels = precision_recall_fscore_support(y_test, y_pred)
    for l, p, r, f in zip(present_labels, precision, recall, f_score):
        print '%s\t%.4lf\t%.4lf\t%.4lf' % (l, p, r, f)

    precision, recall, f_score, support, present_labels = precision_recall_fscore_support(y_test, y_pred, average='macro')
    print 'Macro\t%.4lf\t%.4lf\t%.4lf' % (precision, recall, f_score)
    precision, recall, f_score, support, present_labels = precision_recall_fscore_support(y_test, y_pred, average='micro')
    print 'Micro\t%.4lf\t%.4lf\t%.4lf' % (precision, recall, f_score)

if __name__ == '__main__':
    main()

