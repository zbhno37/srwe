import gzip
import sys
import datetime
import re

def log(logstr, writer = sys.stdout, inline = False):
    writer.write("%s\t%s%s" % (str(datetime.datetime.now()), logstr, '\r' if inline else '\n'))
    writer.flush()

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
    alias_to_name('../../paper/data/freebase/alias_1gram')

if __name__ == '__main__':
    main()
