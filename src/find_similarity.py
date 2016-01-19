import heapq
import logging
from utils import *

logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

def find_most_similarity(word, model):
    heap = MinSizeHeap(20)
    for w in model:
        if word == w: continue
        heap.push((similarity(model[word], model[w]), w))
    heap.sort()
    return heap.arr

def find_most_similarity_vector(vector, model):
    heap = MinSizeHeap(20)
    for w in model:
        heap.push((similarity(vector, model[w]), w))
    heap.sort()
    return heap.arr

def main():
    model = load_w2v_model('../../paper/data/srwe_model/wiki_small.w2v.r.0.0005.model', logging)
    while True:
        query = raw_input('input query word:\n')
        if not query:
            continue
        # words similarity
        #arr = query.strip().split(' ')
        #if len(arr) != 2: continue
        #w1, w2 = arr
        #if w1 not in model or w2 not in model:
            #continue
        #print '%s,%s:%lf' % (w1, w2, similarity(model[w1], model[w2]))

        # top similarity words
        #if query not in model:
            #print '%s not in vocab.' % query
            #continue
        #res = find_most_similarity(query, model)
        #for sim, word in res:
            #print '%s\t%lf' % (word, sim)

        #relation query
        arr = query.strip().split(' ')
        if len(arr) != 2: continue
        w1, w2 = arr
        if w1 not in model or w2 not in model:
            continue
        h_r = [model[w1][i] + model[w2][i] for i in range(len(model[w1]))]
        res = find_most_similarity_vector(h_r, model)
        for sim, word in res:
            print '%s\t%lf' % (word, sim)

if __name__ == '__main__':
    main()
