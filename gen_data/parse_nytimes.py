import os, sys
import datetime
import lxml.etree

def log(logstr, writer = sys.stdout, inline = False):
    writer.write("%s\t%s%s" % (str(datetime.datetime.now()), logstr, '\r' if inline else '\n'))
    writer.flush()

BASE_DIR = '/home/zhangbaihan/Downloads/nytimes/corpus/'
def parse_xml():
    fout = file('../../paper/data/nytimes/nytimes_content', 'w')
    year_list = os.listdir(BASE_DIR)
    count = 0
    for year in year_list:
        for month in range(1, 13):
            ms = '%02d' % month
            path = os.path.join(BASE_DIR, year, ms)
            if not os.path.isdir(path): continue
            days = os.listdir(path)
            for day in days:
                day_path = os.path.join(path, day)
                files = os.listdir(day_path)
                log(day_path)
                for f in files:
                    full_path = os.path.join(day_path, f)
                    doc = lxml.etree.parse(full_path)
                    title = doc.xpath('//body.head')
                    title_text = ''
                    if len(title) != 0:
                        title_text = '\n'.join([x.strip() for x in title[0].itertext() if x.strip()])
                    content = doc.xpath('//body.content')
                    if len(content) == 0: continue
                    text = '\n'.join([x.strip() for x in content[0].itertext() if x.strip()])
                    fout.write('%s\n%s\n' % (title_text.encode('utf-8'), text.encode('utf-8')))
                    if count % 10000 == 0:
                        log(count)
                    count += 1
    fout.close()
    log('total:%d' % total)
def main():
    parse_xml()

if __name__ == '__main__':
    main()
