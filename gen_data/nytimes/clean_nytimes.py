from collections import defaultdict


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
    extract_news()
