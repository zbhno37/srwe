#coding=utf-8
import logging
from gensim.corpora import WikiCorpus
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

def parse_wiki(filename):
    fout = file('../../paper/data/wiki/wiki_corpus', 'w')
    wiki = WikiCorpus(filename, lemmatize=False, dictionary={})
    count = 0
    for text in wiki.get_texts():
        fout.write('%s\n' % ' '.join(text))
        if count % 10000 == 0:
            logging.info(count)
        count += 1

    fout.close()
    logging.info('Finish %d' % count)

def main():
    parse_wiki('../../paper/wiki/enwiki-latest-pages-articles.xml.bz2')

if __name__ == '__main__':
    main()
