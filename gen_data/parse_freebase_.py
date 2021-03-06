import gzip
import sys
sys.path.append('../src')
import datetime
import re
from utils import is_version, load_wiki_dict
import os

def log(logstr, writer = sys.stdout, inline = False):
    writer.write("%s\t%s%s" % (str(datetime.datetime.now()), logstr, '\r' if inline else '\n'))
    writer.flush()

def clean_tag():
    fout = file('../../paper/data/freebase/instance.all.clean', 'w')
    ferr = file('../../paper/data/freebase/instance.all.err', 'w')
    relation = 'type.type.instance>'
    ns_pattern = re.compile(r'<http://rdf.freebase.com/ns/(.*)>')
    count = 1
    with open('../../paper/data/freebase/instance.all.tag') as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if len(arr) != 4 or not arr[1].endswith(relation):
                ferr.write('%s\n' % line)
                continue
            topic = ns_pattern.search(arr[0]).groups()[0]
            mid = ns_pattern.search(arr[2]).groups()[0]
            fout.write('%s\t%s\n' % (topic, mid))
            if count % 100000 == 0:
                log(count)
            count += 1
    fout.close()

def extract_instance():
    fin = gzip.open('../../paper/data/freebase/freebase-rdf-latest.gz.1')
    fout = file('../../paper/data/freebase/os_extract', 'w')

    relation = 'type.type.instance'

    count = 0
    total = 0
    for line in fin:
        if relation in line:
            fout.write('%s' % line)
            count += 1
        if total % 1000000 == 0:
            log('total:%d, count:%d' % (total, count))
        total += 1
    fout.close()
    log('total:%d, count:%d' % (total, count))

def filter_name():
    name_pattern = re.compile(r'\"(.*)\"@en')
    mid_pattern = re.compile(r'<http://rdf.freebase.com/ns/(.*)>')
    fin = gzip.open('../../paper/data/freebase/freebase-rdf-latest.gz.1')
    fout = file('../../paper/data/freebase/mid_name.clean', 'w')

    relation = '<http://rdf.freebase.com/ns/type.object.name>'
    language = '@en'

    count = 0
    total = 0
    for line in fin:
        arr = line.strip().split('\t')
        total += 1
        if len(arr) >= 3 and relation in arr[1] and arr[2].endswith(language):
            name = name_pattern.search(arr[2])
            if not name: continue
            name = name.groups()[0]
            mid = mid_pattern.search(arr[0]).groups()[0]
            fout.write('%s\t%s\n' % (mid, name))
            fout.flush()
            count += 1
            log(count, inline=False)
        if total % 1000000 == 0:
            log('total:%d' % total)

    log('total:%d' % total)
        #if 'type.object.type' in line:
            #fout.write(line)
            #fout.flush()
            #count += 1
            #log(count, inline=False)

def filter_1_gram():
    name_pattern = re.compile(r'\"(.*)\"@en')
    mid_pattern = re.compile(r'<http://rdf.freebase.com/ns/(.*)>')
    fin = open('../../paper/data/freebase/alias')
    fout = open('../../paper/data/freebase/alias_1gram', 'w')
    count = 0
    for line in fin:
        arr = line.strip().split('\t')
        if len(arr) < 3: continue
        name = name_pattern.search(arr[2])
        if not name: continue
        name = name.groups()[0]
        # remain 1 word record
        if len(name.split(' ')) > 1: continue
        mid = mid_pattern.search(arr[0]).groups()[0]
        fout.write('%s\t%s\n' % (mid, name))
        count += 1
        if count % 1000 == 0:
            log(count)
    fout.close()

def load_map(filename):
    id_map = {}
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split('\t')
            id_map[arr[0]] = arr[1]
    return id_map

def alias_to_name(filename):
    count = 1
    log('loading id_map...')
    id_map = load_map('../../paper/data/freebase/id_map.1gram')
    fout = file('../../paper/data/freebase/alias_pair', 'w')
    log('mapping alias...')
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if arr[0] not in id_map: continue
            fout.write('%s\t%s\n' % (id_map[arr[0]], arr[1]))
            if count % 1000 == 0:
                log(count)
    fout.close()

def relation_to_name(filename):
    count = 1
    log('loading id_map...')
    id_map = load_map('../../paper/data/freebase/mid_name')
    fout = file('../../paper/data/freebase/instance.all.name', 'w')
    ferr = file('../../paper/data/freebase/instance.miss.err', 'w')
    log('mapping instances...')
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split('\t')
            if arr[1] not in id_map:
                ferr.write('%s\n' % arr[1])
                continue
            fout.write('%s\t%s\n' % (arr[0], id_map[arr[1]]))
            if count % 1000 == 0:
                log(count)
    fout.close()
    ferr.close()

def split_relation(filename):
    wiki_dict = load_wiki_dict('../../paper/data/wiki/wiki_corpus.vocab')
    count = 1
    fouts = {}
    vocab_in_wiki_count = {}
    with open(filename) as fin:
        for line in fin:
            if count % 10000 == 0:
                log(count)
            count += 1
            arr = line.strip().split('\t')
            if len(arr) != 2: continue
            relation = arr[0].split('.')
            if relation[0] not in fouts:
                fouts[relation[0]] = file('../../paper/data/freebase/split_wiki_words/%s' % relation[0], 'w')
                vocab_in_wiki_count[relation[0]] = {}
                vocab_in_wiki_count[relation[0]]['total'] = 0
                vocab_in_wiki_count[relation[0]]['hit'] = 0
            # rules to extract entity name
            name = None
            parts = arr[1].split(' ')
            if len(parts) == 1: name = arr[1]
            if len(parts) == 2 and is_version(parts[1]): name = parts[0]
            # rules end
            if not name: continue
            name = name.lower()
            vocab_in_wiki_count[relation[0]]['total'] += 1
            if name in wiki_dict: vocab_in_wiki_count[relation[0]]['hit'] += 1
            else: continue
            fouts[relation[0]].write('%s\t%s\t%d\n' % (arr[0], name, wiki_dict[name]))
    fres = file('./hit_rate', 'w')
    for name in fouts:
        fouts[name].close()
        count = vocab_in_wiki_count[name]
        to_write = '%s\thit:%d\ttotal:%d\trate:%lf\n' % (name, count['hit'], count['total'], 1.0 * count['hit'] / (count['total'] if count['total'] != 0 else 1))
        print to_write
        fres.write(to_write)
    fres.close()

def aggregate_topic(path):
    target_topic = [
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
    fout = file('../../paper/data/srwe_model/freebase.100.relation', 'w')
    for topic in target_topic:
        log('processing %s' % topic)
        with open(os.path.join(path, topic)) as fin:
            for line in fin:
                arr = line.strip().split('\t')
                if int(arr[2]) <= 100: continue
                fout.write('%s\t%s\t%s\n' % (arr[1], 'type_of_%s' % topic, topic))
    fout.close()

def main():
    #filter_1_gram()
    #alias_to_name('../../paper/data/freebase/alias_1gram')
    #extract()
    #clean_tag()
    #filter_name()
    #split_relation('../../paper/data/freebase/instance.all.name')
    aggregate_topic('../../paper/data/freebase/split_wiki_words/')

if __name__ == '__main__':
    main()
