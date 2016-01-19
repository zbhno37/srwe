import sys
sys.path.append('../src')
from utils import load_w2v_model, similarity, MinSizeHeap
from collections import defaultdict
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
from multiprocessing import Process

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

def find_similar_word_process(vec, model_items, id, begin, end, top_n, heaps):
    if begin > len(model_items): return
    if end > len(model_items): end = len(model_items)
    for i in range(begin, end):
        if 'type_of_' not in model_items[i][0]:
            heaps[id].push((similarity(vec, model_items[i][1]), model_items[i][0]))
    #for each in heaps[id].arr:
        #print '%d\t%s' % (id, each)

def find_similar_word_multiproc(vec, model_items, top_n = 1, process_nums = 10):
    heaps = [MinSizeHeap(top_n) for i in range(process_nums)]
    #model_items = model.items()
    size = len(model_items) / process_nums
    # seg_info
    # [a, b)
    seg_info = [0]
    for i in range(process_nums - 1):
        seg_info.append(seg_info[-1] + size)
    seg_info.append(len(model_items))
    processes = []
    for i in range(process_nums):
        processes.append(Process(target=find_similar_word_process, args=(vec, model_items, i, seg_info[i], seg_info[i + 1], top_n, heaps)))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    #merge
    heap = MinSizeHeap(top_n)
    for each in heaps:
        heap.extend(each)
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
    model_items = model.items()
    line_count = 0
    with open(test_file) as fin:
        for line in fin:
            #if line_count % 100 == 0:
            logging.info(line_count)
            line_count += 1
            h, r, t = line.strip().split('\t')
            if h not in model: continue
            h_r = add_vector(model[h], model[r])
            #candidates = find_similar_topics(h_r, model, top_n=3)
            candidates = find_similar_word_multiproc(h_r, model_items, top_n=3, process_nums=10)
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
    prediction_res = topic_prediction(test_file, train_file, model)
    for topic in prediction_res:
        res = prediction_res[topic]
        print 'correct:%d, total:%d, correct rate:%lf' % (res['correct'],
                                                         res['total'],
                                                         1.0 * res['correct'] / res['total'])

if __name__ == '__main__':
    main()
