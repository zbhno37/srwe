import heapq
import math

def similarity(v1, v2):
    inner = sum([v1[i] * v2[i] for i in range(len(v1))])
    sum1 = math.sqrt(sum([v1[i] * v1[i] for i in range(len(v1))]))
    sum2 = math.sqrt(sum([v2[i] * v2[i] for i in range(len(v2))]))
    if sum1 == 0 or sum2 == 0:
        return -1
    return inner * 1.0 / (sum1 * sum2)


class MinSizeHeap:
    def __init__(self, size):
        self.size = size
        self.arr = []
        heapq.heapify(self.arr)

    def push(self, item):
        if len(self.arr) > self.size:
            top = self.arr[0]
            if top[0] < item[0]:
                heapq.heappop(self.arr)
                heapq.heappush(self.arr, item)
        else:
            heapq.heappush(self.arr, item)

    def pop(self):
        return heapq.heappop(self.arr)

    def sort(self):
        self.arr.sort(reverse=True)

def load_w2v_model(model_file, logging = None):
    model = {}
    total = 0
    vector_size = 0
    with open(model_file) as fin:
        total, vector_size = map(lambda x: int(x), fin.readline().strip().split(' '))
        if logging:
            logging.info('total:%d, vector_size:%d' % (total, vector_size))
        count = 0
        for line in fin:
            line = line.strip().split(' ')
            model[line[0]] = map(lambda x: float(x), line[1:])
            if count % 10000 == 0 and logging:
                logging.info('loading %d / %d\r' % (count, total))
            count += 1
    return model

