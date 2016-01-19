import sys
sys.path.append('../src')
from utils import load_w2v_model, similarity, MinSizeHeap
from collections import defaultdict
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

def add_vector(vec1, vec2):
    return [vec1[i] + vec2[i] for i in range(len(vec1))]

def minus_vector(vec1, vec2):
    return [vec1[i] - vec2[i] for i in range(len(vec1))]

def find_similar_topics(vec, model, top_n = 1):
    heap = MinSizeHeap(top_n)
    for word in model:
        if 'type_of_' not in word:
            heap.push((similarity(vec, model[word]), word))
    heap.sort()
    return heap.arr

def topic_prediction(test_file, train_file, model):
    # train_file is to calculate relation vector
    k = len(model['</s>'])
    relation_count = defaultdict(lambda: 0)
    with open(train_file) as fin:
        for line in fin:
            h, r, t = line.strip().split('\t')
            if h not in model or t not in model: continue
            if r not in model: model[r] = [0.0] * k
            for i in range(k):
                model[r][i] += model[t][i] - model[h][i]
            relation_count[r] += 1
    for r in relation_count:
        for i in range(k):
            model[r][i] /= relation_count[r]
    return topic_prediction_with_relation(test_file, model)

def topic_prediction_with_relation(test_file, model):
    topic_list = [
        "astronomy",
        "biology",
        "boats",
        "chemistry",
        "computer",
        "fashion",
        "food",
        "geology",
        "interests",
        "language",
    ]
    prediction_res = {}
    for topic in topic_list:
        prediction_res[topic] = {}
        prediction_res[topic]['correct'] = 0
        prediction_res[topic]['total'] = 0

    line_count = 0
    with open(test_file) as fin:
        for line in fin:
            if line_count % 100 == 0:
                logging.info(line_count)
            line_count += 1
            h, r, t = line.strip().split('\t')
            if h not in model: continue
            h_r = add_vector(model[h], model[r])
            candidates = find_similar_topics(h_r, model, top_n=3)
            for simi, topic in candidates:
                if t == topic:
                    prediction_res[t]['correct'] += 1
                    break
            prediction_res[t]['total'] += 1

    return prediction_res

def main():
    model_path = '../../paper/data/srwe_model/wiki_small.w2v.model'
    logging.info('loading model...')
    model = load_w2v_model(model_path, logging)
    train_file = '../../paper/data/srwe_model/freebase.10.relation'
    test_file = '../../paper/data/srwe_model/freebase.computer.relation.test'
    prediction_res = topic_prediction(test_file, test_file, model)
    for topic in prediction_res:
        res = prediction_res[topic]
        print 'correct:%d, total:%d, correct rate:%lf' % (res['correct'],
                                                         res['total'],
                                                         1.0 * res['correct'] / res['total'])

if __name__ == '__main__':
    main()
