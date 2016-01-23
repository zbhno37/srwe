import sys
sys.path.append('../src')
from utils import load_w2v_model, similarity, MinSizeHeap, similarity_numpy
from collections import defaultdict
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager

class HeapManager(BaseManager):
    pass

HeapManager.register('MinSizeHeap', MinSizeHeap, exposed = ['push', 'pop', 'sort', 'extend', 'clear', 'get'])

def add_vector(vec1, vec2):
    return [vec1[i] + vec2[i] for i in range(len(vec1))]
    #return vec1 + vec2

def minus_vector(vec1, vec2):
    #return [vec1[i] - vec2[i] for i in range(len(vec1))]
    return vec1 - vec2

def find_similar_topics(vec, model, top_n = 1):
    heap = MinSizeHeap(top_n)
    for word in model:
        if 'type_of_' not in word:
            heap.push((similarity(vec, model[word]), word))
            #heap.push((similarity_numpy(vec, model[word]), word))
        heap.sort()
    return heap.arr

def get_lc_and_relation(filename):
    count = 0
    relation = set()
    with open(filename) as fin:
        for line in fin:
            count += 1
            relation.add(line.strip().split('\t')[-1])
    return count, list(relation)

def find_similar_word_process(vec, model_items, _id, begin, end, top_n, heap):
    heap.clear()
    if begin > len(model_items): return
    if end > len(model_items): end = len(model_items)
    for i in range(begin, end):
        if 'type_of_' not in model_items[i][0]:
            heap.push((similarity(vec, model_items[i][1]), model_items[i][0]))
    #for each in heap.get():
        #print '%d\t%s' % (_id, each)

def find_similar_word_multiproc(vec, model_items, heaps, top_n = 1, process_nums = 10):
    size = len(model_items) / process_nums
    # seg_info
    # [a, b)
    seg_info = [0]
    for i in range(process_nums - 1):
        seg_info.append(seg_info[-1] + size)
    seg_info.append(len(model_items))
    processes = []
    for i in range(process_nums):
        processes.append(Process(target=find_similar_word_process, args=(vec, model_items, i, seg_info[i], seg_info[i + 1], top_n, heaps[i])))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    #merge
    heap = MinSizeHeap(top_n)
    for each in heaps:
        heap.extend(each.get())
    heap.sort()
    return heap.arr

def topic_prediction(test_file, train_file, model):
    # train_file is to calculate relation vector
    k = len(model['</s>'])
    relation_count = defaultdict(lambda: 0)
    logging.info('calculating relation vectors...')
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
    #return topic_prediction_with_relation(test_file, model)
    return topic_prediction_with_relation_multiproc(test_file, model)

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
        # 1 for smooth
        prediction_res[topic]['total'] = 1
    model_items = model.items()
    line_count = 0
    process_nums = 10
    top_n = 3

    heapManager = HeapManager()
    heapManager.start()
    heaps = [None] * process_nums
    for i in range(process_nums):
        heaps[i] = heapManager.MinSizeHeap(top_n)

    with open(test_file) as fin:
        for line in fin:
            #if line_count % 100 == 0:
            logging.info(line_count)
            line_count += 1
            h, r, t = line.strip().split('\t')
            if h not in model: continue
            h_r = add_vector(model[h], model[r])
            #candidates = find_similar_topics(h_r, model, top_n=3)
            candidates = find_similar_word_multiproc(h_r, model_items, heaps=heaps, top_n=top_n, process_nums=process_nums)
            for simi, topic in candidates:
                if t == topic:
                    prediction_res[t]['correct'] += 1
                    break
            prediction_res[t]['total'] += 1

    return prediction_res

def find_similar_word_partly_proc(_id, topic_list, filename, model, begin, end, count_dict, top_n):
    logging.info('process %d start' % _id)
    # not dict(dict())
    # the inner dict can not be sync
    #for topic in topic_list:
        #logging.info('%d, topic:%s' % (_id, topic))
        ##count_dict[topic] = {}
        ##count_dict[topic][1] = 0
        ##count_dict[topic][3] = 0
        ##count_dict[topic][5] = 0
        ##count_dict[topic][0] = 1
    line_count = 0
    process_line = 0
    with open(filename) as fin:
        for line in fin:
            line_count += 1
            if line_count < begin: continue
            if line_count >= end: break
            process_line += 1
            #if process_line > 10: break
            if process_line % 10 == 0:
                logging.info('process %d:%d:%lf%%' % (_id, process_line, 1.0 * process_line / (end - begin) * 100))
            h, r, t = line.strip().split('\t')
            if h not in model: continue
            h_r = add_vector(model[h], model[r])
            #h_r = model[h] + model[r]
            candidates = find_similar_topics(h_r, model, top_n=top_n)
            for i, each in enumerate(candidates):
                simi, topic = each
                if t == topic:
                    if i == 0:
                        count_dict['%s_1' % topic] += 1
                        count_dict['%s_3' % topic] += 1
                        count_dict['%s_5' % topic] += 1
                        #count_dict[topic][1] += 1
                        #count_dict[topic][3] += 1
                        #count_dict[topic][5] += 1
                    elif 1 <= i <= 2:
                        count_dict['%s_3' % topic] += 1
                        count_dict['%s_5' % topic] += 1
                        #count_dict[topic][3] += 1
                        #count_dict[topic][5] += 1
                    elif 3<= i <= 4:
                        count_dict['%s_5' % topic] += 1
                        #count_dict[topic][5] += 1
                    break
            count_dict['%s_0' % t] += 1
    logging.info('process %d finished.' % _id)

def topic_prediction_with_relation_multiproc(test_file, model):
    total = 0
    process_nums = 10
    top_n = 5
    logging.info('geting line count...')
    total, topic_list = get_lc_and_relation(test_file)
    size = total / process_nums
    seg_info = [0]
    for i in range(process_nums - 1):
        seg_info.append(seg_info[-1] + size)
    seg_info.append(total)

    manager = Manager()
    count_dicts = []
    for i in range(process_nums):
        count_dicts.append(manager.dict())
        for topic in topic_list:
            count_dicts[i]['%s_1' % topic] = 0
            count_dicts[i]['%s_3' % topic] = 0
            count_dicts[i]['%s_5' % topic] = 0
            count_dicts[i]['%s_0' % topic] = 0
    processes = []
    for i in range(process_nums):
        processes.append(Process(target=find_similar_word_partly_proc, args=(i, topic_list, test_file, model, seg_info[i], seg_info[i + 1], count_dicts[i], top_n)))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    prediction_res = {}
    for topic in topic_list:
        prediction_res[topic] = {}
        prediction_res[topic][1] = 0
        prediction_res[topic][3] = 0
        prediction_res[topic][5] = 0
        prediction_res[topic][0] = 0

    for count_dict in count_dicts:
        for topic in topic_list:
            for i in [0, 1, 3, 5]:
                key = '%s_%d' % (topic, i)
                prediction_res[topic][i] += count_dict[key]

    for topic in topic_list:
        if prediction_res[topic][0] == 0:
            prediction_res[topic][0] = 1
    return prediction_res

def main():
    has_relation = False
    model_path = '../../paper/data/srwe_model/wiki_small.w2v.model'
    #model_path = '../../paper/data/srwe_model/wiki_small.w2v.model'
    logging.info('loading model...')
    model = load_w2v_model(model_path, logging, nparray=False)
    train_file = '../../paper/data/srwe_model/freebase.100.relation.train'
    test_file = '../../paper/data/srwe_model/freebase.100.relation.test'
    if has_relation:
        #prediction_res = topic_prediction_with_relation(test_file, model)
        prediction_res = topic_prediction_with_relation_multiproc(test_file, model)
    else:
        #prediction_res = topic_prediction(test_file, train_file, model)
        prediction_res = topic_prediction(test_file, train_file, model)

    total_count = {}
    for i in [0, 1, 3, 5]:
        total_count[i] = 0

    for topic in prediction_res:
        res = prediction_res[topic]
        print 'topic:%s, total:%d' % (topic, res[0])
        total_count[0] += res[0]
        for i in range(1, 6):
            if i in res:
                total_count[i] += res[i]
                print 'top:%d, correct:%d, total:%d, correct rate:%lf' % (
                            i, res[i], res[0], 1.0 * res[i] / res[0])
        #print 'correct:%d, total:%d, correct rate:%lf' % (res['correct'],
                                                         #res['total'],
                                                         #1.0 * res['correct'] / res['total'])
    print 'total'
    for i in range(1, 6):
        if i in total_count:
            print 'top:%d, correct:%d, total:%d, correct rate:%lf' % (
                i, total_count[i], total_count[0], 1.0 * total_count[i] / total_count[0])
if __name__ == '__main__':
    main()
