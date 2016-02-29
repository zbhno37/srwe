# -*- coding: utf-8 -*-
import urllib2, cookielib
import lxml.html as H
import socket
socket.setdefaulttimeout(5)
from time import sleep
from datetime import datetime
from Queue import Queue, Empty
import threading
import sys

HOST = "http://spiderbites.nytimes.com/"
XPATH_NEWS = '//ul[@id="headlines"]/li/a/@href'
XPATH_CATEGORY = '//meta[@property="article:section"]/@content'
XPATH_TITLE = '//meta[@property="og:title"]/@content'
XPATH_ABSTRACT = '//meta[@property="og:description"]/@content'
XPATH_DATE = '//meta[@property="article:published"]/@content'

class Requester:
    UR_KEY = 'User-Agent'
    UR_VALUE = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65'

    def __init__(self, timeout = 5):
        self.timeout = timeout
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    def get(self, url):
        #req = urllib2.Request(url)
        #req.add_header(self.UR_KEY, self.UR_VALUE)
        #content = urllib2.urlopen(req, timeout=self.timeout).read()
        return self.opener.open(url).read()


def log(logstr, writer = sys.stdout):
    writer.write("%s\t%s\n" % (str(datetime.now()), logstr))
    writer.flush()

def fetch_news_urls(filename):
    requester = Requester()
    fout = file('%s_news_url' % sys.argv[1], 'w')
    with open(filename) as fin:
        for line in fin:
            url = HOST + line.strip()
            print url
            html = requester.get(url)
            page = H.document_fromstring(html)
            news_node = page.xpath(XPATH_NEWS)
            for news in news_node:
                fout.write('%s\n' % str(news))
    fout.close()

def load_list(filename):
    ls = []
    with open(filename) as fin:
        for line in fin:
            ls.append(line.strip())
    return ls

def dump_queue(queue):
    with open('queue_%s.dump' % sys.argv[1], 'w') as fout:
        while not queue.empty():
            item, count = queue.get(False)
            fout.write(item + '\n')


def fetch_news_info_thread(requester, queue, index):
    fout = file('./%s_news_part/news.part.%d' % (sys.argv[1], index), 'a')
    ferr = file('./%s_news_part/news.err.part.%d' % (sys.argv[1], index), 'a')
    failure_count = 0
    while not queue.empty():
        try:
            url, count = queue.get(True, 30)
            if count > 10:
                log('REQ_ERROR:%s' % url, ferr)
                continue
            html = requester.get(url)
            log('%s\tfetched' % url)
            page = H.document_fromstring(html)
            category = page.xpath(XPATH_CATEGORY)
            date = page.xpath(XPATH_DATE)
            title = page.xpath(XPATH_TITLE)
            abstract = page.xpath(XPATH_ABSTRACT)
            if len(category) < 1 or (len(title) < 1 and len(abstract) < 1): continue
            title_str = title[0].encode('utf-8') if len(title) > 0 else ''
            abstract_str = abstract[0].encode('utf-8') if len(abstract) > 0 else ''
            date_str = date[0].encode('utf-8') if len(date) > 0 else ''
            fout.write('%s\t%s\t%s\t%s\t%s\n' % (url, category[0].encode('utf-8'), title_str, date_str, abstract_str))
            fout.flush()
            failure_count = 0
        except Empty:
            log('EMPTY:%d' % index, ferr)
            break
        except (urllib2.URLError, socket.timeout, socket.error, urllib2.HTTPError):
            queue.put((url, count + 1))
            failure_count += 1
            if failure_count == 10:
                log('TIMEOUT:%d' % index, ferr)
                sleep(10 * failure_count)
            elif failure_count >= 20:
                log('NETWORK_ERR:%d' % index, ferr)
                break
    log('Thread %s done' % index)
    fout.close()
    ferr.close()

def crawle_news_info():
    requester = Requester()
    queue = Queue()
    urls = load_list('./%s_news_url' % sys.argv[1])
    #urls = load_list('./queue.dump')
    log('urls to fetch:%s' % len(urls))
    for url in urls:
        queue.put((url, 1))
    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=fetch_news_info_thread, args=(requester, queue, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if not queue.empty():
        dump_queue(queue)
    log('Finish')

def main():
    fetch_news_urls('./%s_url' % sys.argv[1])
    crawle_news_info()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        log('argv error')
        exit(1)
    main()
