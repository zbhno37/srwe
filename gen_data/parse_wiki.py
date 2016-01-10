#coding=utf-8
import logging
from gensim.corpora import WikiCorpus
from collections import defaultdict
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

def parse_wiki(filename):
    fout = file('../../paper/data/wiki/wiki_corpus', 'w')
    wiki = WikiCorpus(filename, lemmatize=False, dictionary={}, processes=5)
    count = 0
    for text in wiki.get_texts():
        fout.write('%s\n' % ' '.join(text))
        if count % 10000 == 0:
            logging.info(count)
        count += 1

    fout.close()
    logging.info('Finish %d' % count)

def word_freq(filename):
    fout = file('../../paper/data/wiki/wiki_corpus.vocab', 'w')
    freq = defaultdict(lambda: 0)
    count = 0
    with open(filename) as fin:
        for line in fin:
            words = line.strip().split(' ')
            for word in words:
                freq[word] += 1
            if count % 10000 == 0:
                logging.info(count)
            count += 1
    sorted_words = sorted(freq.items(), key=lambda x:x[1], reverse=True)
    for item in sorted_words:
        fout.write('%s\t%s\n' % (item[0], item[1]))
    fout.close()

def main():
    #parse_wiki('../../paper/data/wiki/enwiki-latest-pages-articles.xml.bz2')
    word_freq('../../paper/data/wiki/wiki_corpus')

if __name__ == '__main__':
    main()
