from collections import defaultdict
import sys
sys.path.append('../../evaluation/')
sys.path.append('../../src/')
from text_classification import clean_text

def count_category():
    category_count = defaultdict(lambda: 0)
    with open('./nytimes.2010_2015') as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if len(arr) != 5: continue
            category_count[arr[1]] += 1

    sorted_category = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_category:
        print category, count

def count_category_and_char():
    category_count = defaultdict(lambda: 0)
    category_word_count = defaultdict(lambda: 0)
    with open('./news_corpus') as fin:
        for line in fin:
            arr = line.strip().split('\t')
            category_count[arr[1]] += 1
            #category_word_count[arr[1]] += len(clean_text(arr[0].decode('utf-8')))
    sorted_category = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
    #print ' & '.join(map(lambda x: '%d' % x[1], sorted_category))
    for category, count in sorted_category:
        print '\\hline'
        print '%s & %d \\\\' % (category, count)

def load_category(filename):
    category_map = {}
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split('\t')
            for cate in arr[1:]:
                category_map[cate] = arr[0]
    return category_map


def extract_news():
    category_map = load_category('./category_mapping.txt')
    category_count = defaultdict(lambda: 0)
    fout = file('./news_corpus', 'w')
    with open('./nytimes.2010_2015') as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if len(arr) != 5: continue
            category = category_map.get(arr[1], None)
            if not category: continue
            fout.write('%s %s\t%s\n' % (arr[2], arr[4], category))
            category_count[category] += 1
    for category in category_count:
        print category, category_count[category]
    fout.close()

if __name__ == '__main__':
    #extract_news()
    count_category_and_char()
