import re
import logging

logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

pattern = re.compile(r'[\'\"\\,./;\[\]<>?:\{\}|!~`@#$^&*()_]')

fout = file('../../paper/data/nytimes/nytimes_corpus', 'w')

count = 0
with open('../../paper/data/nytimes/nytimes_content') as fin:
    for line in fin:
        fout.write('%s' % (pattern.sub(' ', line.lower())))
        if count % 100000 == 0:
            logging.info(count)
        count += 1

fout.close()

