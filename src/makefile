CC = g++
#The -Ofast might not work with older versions of gcc; in that case, use -O2
CFLAGS = -lm -pthread -Ofast -march=native -Wall -funroll-loops -Wno-unused-result -std=c++11

OBJS = Paraphrase.o

all: word2vec_joint

%.o : %.cpp
	$(CC) -c $< -o $@ $(CFLAGS)

word2vec_joint : word2vec_joint.cpp $(OBJS)
	$(CC) word2vec_joint.cpp $(OBJS) -o word2vec_joint $(CFLAGS)

clean:
	rm -rf word2vec_joint *.o
