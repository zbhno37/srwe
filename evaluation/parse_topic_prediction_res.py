import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'argv error'
        print 'argv: filename'
    filename = sys.argv[1]
    with open(filename) as fin:
        while True:
            line = fin.readline()
            if not line: break

            if line.startswith('topic') or line.startswith('total'):
                topic = line.strip() if line.startswith('total') else line.strip().split(',')[0].split(':')[1]
                line = fin.readline()
                arr = line.strip().split(',')
                precision = float(arr[-1].strip().split(':')[-1])
                print '%s\t%.4lf' % (topic, precision)
