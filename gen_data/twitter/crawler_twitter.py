import lxml.html as H
import urllib
import socket
socket.setdefaulttimeout(10)
import json
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
from multiprocessing import Process

XPATH_INITDATA = '//p[@class="TweetTextSize TweetTextSize--26px js-tweet-text tweet-text"]'

def get_tweet(uid, sid):
    f = urllib.urlopen("https://twitter.com/%s/status/%s" % (uid, sid))
    page = H.document_fromstring(f.read())
    node = page.xpath(XPATH_INITDATA)
    if len(node) != 1: return None
    return node[0].text_content()
    #data = json.loads(node[0].value)
    #if u'initialState' not in data or u'title' not in data[u'initialState']: return None
    #return data[u'initialState'][u'title']

def work_process(_id, begin, end, filename):
    logging.info('process %d start' % _id)
    fout = file('../tweets/part_%d.res' % _id, 'w')
    ferr = file('../tweets/part_%d.err' % _id, 'w')
    line_count = 0
    process_line = 0
    with open(filename) as fin:
        for line in fin:
            line_count += 1
            if line_count < begin: continue
            if line_count >= end: break
            process_line += 1
            if process_line % 10 == 0:
                logging.info('process %d:%d:%lf%%' % (_id, process_line, 1.0 * process_line / (end - begin) * 100))
            sid, uid, md5, topic = line.strip().split('\t')
            try:
                tweet = get_tweet(uid, sid)
                if tweet:
                    fout.write('%s\t%s\t%s\t%s\n' % (sid, uid, topic, tweet.encode('utf-8')))
                    fout.flush()
            except Exception, e:
                logging.info('process:%d\tline:%d\terr:%s' % (_id, line_count, str(e)))
                ferr.write('%s' % line)
                ferr.flush()
    fout.close()
    ferr.close()
    logging.info('process:%d finish' % _id)

def get_line_count(filename):
    logging.info('getting line count')
    count = 0
    with open(filename) as fin:
        for line in fin:
            count += 1
    return count

def main():
    filename = '../../../paper/data/twitter/ODPtweets-Mar17-29.tsv'
    total = get_line_count(filename)
    logging.info('%s:line_count:%d' % (filename, total))
    process_nums = 5
    size = total / process_nums
    seg_info = [0]
    for i in range(process_nums - 1):
        seg_info.append(seg_info[-1] + size)
    seg_info.append(total)
    processes = []
    for i in range(process_nums):
        processes.append(Process(target=work_process, args=(i, seg_info[i], seg_info[i + 1], filename, )))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    main()

