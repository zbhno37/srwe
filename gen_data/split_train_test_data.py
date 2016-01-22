import random
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
from collections import defaultdict

def sample_all(filename):
    logging.info('split_train_test_data:sample_all: %s' % filename)
    test_percentage = 10
    fout_train = file('%s.train' % filename, 'w')
    fout_test = file('%s.test' % filename, 'w')
    count = 0
    with open(filename) as fin:
        for line in fin:
            if count % 1000 == 0: logging.info(count)
            count += 1
            num = random.randint(1, 100)
            if num <= test_percentage:
                fout_test.write('%s\n' % line.strip())
            else:
                fout_train.write('%s\n' % line.strip())
    fout_test.close()
    fout_train.close()

def sample_by_relation(filename):
    logging.info('split_train_test_data:sample_by_relation: %s' % filename)
    test_percentage = 20
    fout_train = file('%s.train' % filename, 'w')
    fout_test = file('%s.test' % filename, 'w')
    count = 0
    relation_list = defaultdict(list)
    with open(filename) as fin:
        for line in fin:
            if count % 1000 == 0: logging.info(count)
            count += 1
            arr = line.strip().split('\t')
            h, r, t = arr
            relation_list[r].append(arr)
            #num = random.randint(1, 100)
            #if num <= test_percentage:
                #fout_test.write('%s\n' % line.strip())
            #else:
                #fout_train.write('%s\n' % line.strip())
    for relation in relation_list:
        logging.info('%s, size:%d' % (relation, len(relation_list[relation])))
        random.shuffle(relation_list[relation])
        test_size = len(relation_list[relation]) * test_percentage / 100
        for i in range(len(relation_list[relation])):
            if i <= test_size:
                fout_test.write('%s\n' % '\t'.join(relation_list[relation][i]))
            else:
                fout_train.write('%s\n' % '\t'.join(relation_list[relation][i]))
    fout_test.close()
    fout_train.close()

def main():
    filename = '../../paper/data/srwe_model/freebase.100.relation'
    #sample_all(filename)
    sample_by_relation(filename)

if __name__ == '__main__':
    main()
