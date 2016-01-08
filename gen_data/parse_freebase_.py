import gzip
import sys
import datetime
import re

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

def filter():
    fin = gzip.open('../../paper/data/freebase/freebase-rdf-latest.gz.1')
    fout = file('../../paper/data/freebase/mid_name', 'w')

    relation = '<http://rdf.freebase.com/ns/type.object.name>'
    language = '@en'

    count = 0
    total = 0
    for line in fin:
        arr = line.strip().split('\t')
        total += 1
        if len(arr) >= 3 and relation in arr[1] and arr[2].endswith(language):
            fout.write(line)
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

def main():
    #filter_1_gram()
    #alias_to_name('../../paper/data/freebase/alias_1gram')
    #extract()
    clean_tag()

if __name__ == '__main__':
    main()
