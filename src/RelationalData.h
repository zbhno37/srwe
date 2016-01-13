#ifndef RELATIONALDATA_H
#define RELATIONALDATA_H

#include <unordered_map>
#include <unordered_set>
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <vector>
#include <iostream>
using namespace std;

class RelationalData {
public:
    unordered_map<string, vector<pair<string, string>>> dataset;
    unordered_map<string, int> relations;

    RelationalData(const string& filename) {
        ReadData(filename);
    }

    void ReadData(const string& filename);

};

void RelationalData::ReadData(const string& filename) {
    // file format
    // head relation tail (instance relation topic)
    // example
    // dos type_of_computer(or operating_system) computer
    //
    ifstream fin(filename.c_str());
    string line, head, relation, tail;
    while (getline(fin, line)) {
        istringstream iss(line);
        iss >> head >> relation >> tail;
        dataset[head].push_back(pair<string, string>(relation, tail));
        relations[relation]++;
        //if (dataset[head].size() > 1)
            //cout << head << endl;
    }
    fin.close();
}

#endif
