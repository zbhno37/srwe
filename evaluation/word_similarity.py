import scipy.stats
import sys
sys.path.append('../src')
from utils import load_w2v_model, similarity

import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
import random

def load_standard(filename):
    word_pair = []
    simi = []
    with open(filename) as fin:
        for line in fin:
            if line.strip().startswith('#'): continue
            arr = line.strip().split('\t')
            if len(arr) != 4: continue
            word_pair.append((arr[1].lower(), arr[2].lower()))
            simi.append(float(arr[3]))
    return word_pair, simi

def main():
    word_pair, simi = load_standard('./wordsim353_annotator1.txt')
    #model = load_w2v_model('../../paper/word2vec/vec.txt', logging)
    model_path = '../../paper/data/srwe_model/wiki_small.w2v.r.0.001.model'
    model = load_w2v_model(model_path, logging)
    new_simi = []
    for pair in word_pair:
        if pair[0] not in model or pair[1] not in model:
            logging.error('%s not in vocab.' % pair[0] if pair[0] not in model else pair[1])
            new_simi.append(0.0)
            continue
        new_simi.append(similarity(model[pair[0]], model[pair[1]]))
    print model_path
    res = scipy.stats.spearmanr(simi, new_simi)
    print res

if __name__ == '__main__':
    main()
