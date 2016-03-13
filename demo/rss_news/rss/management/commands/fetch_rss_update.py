from django.core.management.base import BaseCommand, CommandError
from rss.models import RSSItem, ClassItem, Subscription, News
import time
from dateutil import parser as time_parser
import feedparser
import logging
from sklearn.externals import joblib
logger = logging.getLogger('django_logger')
fetch_logger = logging.getLogger('fetch_logger')
import sys
#sys.path.append('../../../../../src')
#sys.path.append('../../../../../evaluation/')
sys.path.append('/home/zhangbaihan/srwe/src')
sys.path.append('/home/zhangbaihan/srwe/evaluation/')
from text_classification import clean_text, get_vec_len, get_vec_from_words
from utils import load_w2v_model

clfs = {}
w2v_model = {}
dimension = 0

def classfy(w2v_model, clfs, text):
    fetch_logger.info('classfying:text:%s' % text)
    vec = get_vec_from_words(clean_text(text.decode('utf-8')), w2v_model, dimension)
    pred_res = []
    for label in clfs:
        pred_res.append((clfs[label].predict_proba(vec.reshape(1, -1))[0][1], label))
    sorted_pred = sorted(pred_res, key=lambda x: x[0], reverse=True)
    fetch_logger.info('label:%s' % sorted_pred[0][1])
    return sorted_pred[0][1]

def format_time(secs):
    return time.strftime('%Y-%m-%d %H:%M:%S', secs)

def get_classes():
    labels = {}
    classes = ClassItem.objects.all()
    for item in classes:
        labels[item.title.encode('utf-8')] = item
    return labels

def load_models(labels):
    global clfs, w2v_model, dimension
    path = '/home/zhangbaihan/srwe/evaluation/clf_model/%s.model'
    model_file = '/home/zhangbaihan/paper/data/srwe_model/wiki_small.w2v.100.r.0.00001.s.0.00009.model'
    if not clfs:
        keys = labels.keys()
        fetch_logger.info('loadding LR models...')
        for label in keys:
            fetch_logger.info('loadding %s.model ...' % label)
            clfs[label] = joblib.load(path % label)
    if not w2v_model:
        fetch_logger.info('loadding w2v model...')
        w2v_model = load_w2v_model(model_file, None, nparray=True)
    dimension = get_vec_len(w2v_model)

def fetch_rss_update():
    fetch_logger = logging.getLogger('fetch_logger')
    fetch_logger.info('#########fetch cron begin...###########')
    labels = get_classes()
    if not clfs or not w2v_model: load_models(labels)

    rss_items = RSSItem.objects.all()
    for item in rss_items:
        url = item.url
        update_time = item.update_time
        #update_time = item.update_time.timetuple()
        latest = update_time
        fetch_logger.info('%s,%s' % (url, update_time))
        parser = feedparser.parse(url)
        for entry in parser.entries:
            published_datetime = time_parser.parse(entry.published)
            if latest < published_datetime:
                latest = published_datetime
            if update_time >= published_datetime:
                break
            title = entry['title'].encode('utf-8')
            abstract = entry['summary'].encode('utf-8')
            url = entry['link'].encode('utf-8')
            # Do classification
            label = classfy(w2v_model, clfs, '%s %s' % (title, abstract))
            class_item = labels[label]
            new_news = News(rss_id=item, pub_time=published_datetime, title=title, abstract=abstract, content='', news_link=url, class_id=class_item)
            new_news.save()

        if latest > update_time:
            item.update_time = latest
            item.save()
    fetch_logger.info('#########fetch cron end###########')
    #return HttpResponse('successfully')

class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_rss_update()
        #print 'hello world'

