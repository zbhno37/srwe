import random
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

def sample_all(filename):
    logging.info('split_train_test_data: %s' % filename)
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

def main():
    filename = '../../paper/data/srwe_model/freebase.computer.relation'
    sample_all(filename)

if __name__ == '__main__':
    main()
