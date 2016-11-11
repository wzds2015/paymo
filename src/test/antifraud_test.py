#! /usr/bin/env python

"""
    Filename: antifraud_test.py
    Author: Wenliang Zhao
    Email: wz927@nyu.edu
    Created: 11/10/2016
    Last Modified: 11/10/2016
"""

import numpy as np
from itertools import chain, imap
import time, os, unittest 

"""
    Purpose: read a text file name, output a list with tuples. 
             Tuple is column 2 and 3 which are id1 and id2
    @inputs: filename: input file name as string
    @outputs: res_list: output list (edges of degree1 graph)
"""
def read_input(filename):
    res_list = []
    with open(filename) as infile:
        next(infile)
        for l in infile:
            tmp_list = l.split(',', 4)
            id1, id2 = tmp_list[1].strip(), tmp_list[2].strip()
            res_list.append((id1, id2))
    infile.close()
    return res_list

"""
    Purpose: apply a function on a iterable and flatten final results
    @inputs: f: a function; items: an iterable
    @outputs: the flatten iterable whose elements is results after applying the function
"""
def flatMap(f, items):
    return chain.from_iterable(imap(f, items))

"""
    Purpose: read a input edges list, output a map representing a graph
    @inputs: input_list: edge list
	@outputs: res_dict: dictionary for degree1 graph
"""
def build_degree1_graph(input_list):
    res_dict = {}
    for tp in input_list:
        if not res_dict.has_key(tp[0]):
            res_dict[tp[0]] = [tp[1]]
        else:
            if tp[1] not in res_dict[tp[0]]:
                res_dict[tp[0]].append(tp[1])

        if not res_dict.has_key(tp[1]):
            res_dict[tp[1]] = [tp[0]]
        else:
            if tp[0] not in res_dict[tp[1]]:
                res_dict[tp[1]].append(tp[0])
    return res_dict

"""
    Purpose: read a degree1 map, output a degree2 map
    @inputs: d1_dict: degree1 map
    @outputs: res_dict: degree2 map 
"""
def build_degree2_graph(d1_dict):
    res_dict = {}
    for k, v in d1_dict.items():
        res_dict[k] = set(flatMap(lambda x: d1_dict[x], v)).difference(set(v))
    return res_dict

"""
    Purpose: convert neighbor lists to sets
	@inputs: d1_dict: degree1 map
    @outputs: d1_dict: degree1 map but values has been change to sets
"""
def dict_list2set(d1_dict):
    for k in d1_dict.keys():
        d1_dict[k] = set(d1_dict[k])
    return d1_dict

"""
    Purpose: check if target user is in the degree1 connection of source user
    @inputs: src: source user
             dst: target user
             d1_dict: degree1 map
    @outputs: string -- 'trusted' or 'unverified'
"""
def inDegree1(src, dst, d1_dict):
    if d1_dict.has_key(src) and dst in d1_dict[src]:
        return 'trusted'
    return 'unverified'

"""
    Purpose: check if target user is in the degree2 connection of source user
    @inputs: src: source user
             dst: target user
             d2_dict: degree2 map
    @outputs: string -- 'trusted' or 'unverified'
"""
def inDegree2(src, dst, d2_dict):
    if d2_dict.has_key(src) and dst in d2_dict[src]:
        return 'trusted'
    return 'unverified'

"""
    Purpose: check if target user is in the degree3/4 connection of source user
    @inputs: src: source user
             dst: target user
             d1_dict: degree1 map
             d2_dict: degree2 map
    @outputs: string -- 'trusted' or 'unverified'
"""
def inDegree4(src, dst, d1_dict, d2_dict):
    if (not d1_dict.has_key(src)) or (not d1_dict.has_key(dst)):
        return 'unverified'
    degree1_src = d1_dict[src]
    degree2_src = d2_dict[src]
    degree2_dst = d2_dict[dst]
    for s in degree2_dst:
        if (s in degree1_src) or (s in degree1_src):
            return 'trusted'
    return 'unverified'

"""
    Purpose: implement feature1
    @inputs: trans_file: new transaction file name
             output_file: output file name
             d1_dict: degree1 map
"""
def feature1(trans_file, output_file, d1_dict):
    with open(trans_file, 'r') as infile, open(output_file, 'w') as outfile:
        next(infile)
        for l in infile:
            src = l.split(',', 4)[1].strip()
            dst = l.split(',', 4)[2].strip()
            outfile.write(inDegree1(src, dst, d1_dict)+'\n')
	infile.close()
    outfile.close()

"""
    Purpose: implement feature2
    @inputs: trans_file: new transaction file name
             output_file: output file name
             d1_dict: degree1 map
             d2_dict: degree2 map
"""
def feature2(trans_file, output_file, d1_dict, d2_dict):
    with open(trans_file, 'r') as infile, open(output_file, 'w') as outfile:
        next(infile)
        for l in infile:
            src = l.split(',', 4)[1].strip()
            dst = l.split(',', 4)[2].strip()
            if (inDegree1(src, dst, d1_dict) == 'trusted') or (inDegree2(src, dst, d2_dict) == 'trusted'):
                outfile.write('trusted\n')
            else:
                outfile.write('unverified\n')
    infile.close()
    outfile.close()

"""
    Purpose: implement feature3
    @inputs: trans_file: new transaction file name
             output_file: output file name
             d1_dict: degree1 map
             d2_dict: degree2 map
"""
def feature3(trans_file, output_file, d1_dict, d2_dict):
    with open(trans_file, 'r') as infile, open(output_file, 'w') as outfile:
        next(infile)
        for l in infile:
            src = l.split(',', 4)[1].strip()
            dst = l.split(',', 4)[2].strip()
            if (inDegree1(src, dst, d1_dict) == 'trusted') or (inDegree2(src, dst, d2_dict) == 'trusted') or (inDegree4(src, dst, d1_dict, d2_dict) == 'trusted'):
                outfile.write('trusted\n')
            else:
                outfile.write('unverified\n')
    infile.close()
    outfile.close()

class TestAntifraud(unittest.TestCase):
    def test_feature1(self):
        print "Unit test for feature1"
        project_dir = os.getcwd()
        batch_file = project_dir + '/paymo_input/batch_payment_test.csv'
        stream_file = project_dir + '/paymo_input/stream_payment_test.csv'
        outfile1 = project_dir + '/paymo_output/output1_test.txt'
        degree1_graph = build_degree1_graph(read_input(batch_file))
        feature1(stream_file, outfile1, degree1_graph)
        out = open(outfile1, 'r')
        result = map(lambda x: x.strip(), out.readlines())
        self.assertSequenceEqual(result, ['unverified', 'unverified', 'unverified' ,'unverified'])

    def test_feature2(self):
        print "Unit test for feature2"
        project_dir = os.getcwd()
        batch_file = project_dir + '/paymo_input/batch_payment_test.csv'
        stream_file = project_dir + '/paymo_input/stream_payment_test.csv'
        outfile2 = project_dir + '/paymo_output/output2_test.txt'
        degree1_graph = build_degree1_graph(read_input(batch_file))
        degree2_graph = build_degree2_graph(degree1_graph)
        degree1_graph = dict_list2set(degree1_graph)
        feature2(stream_file, outfile2, degree1_graph, degree2_graph)
        out = open(outfile2, 'r')
        result = map(lambda x: x.strip(), out.readlines())
        self.assertSequenceEqual(result, ['trusted', 'unverified', 'unverified', 'unverified'])

    def test_feature3(self):
        print "Unit test for feature3"
        project_dir = os.getcwd()
        batch_file = project_dir + '/paymo_input/batch_payment_test.csv'
        stream_file = project_dir + '/paymo_input/stream_payment_test.csv'
        outfile3 = project_dir + '/paymo_output/output2_test.txt'
        degree1_graph = build_degree1_graph(read_input(batch_file))
        degree2_graph = build_degree2_graph(degree1_graph)
        degree1_graph = dict_list2set(degree1_graph)
        feature3(stream_file, outfile3, degree1_graph, degree2_graph)
        out = open(outfile3, 'r')
        result = map(lambda x: x.strip(), out.readlines())
        self.assertSequenceEqual(result, ['trusted', 'unverified', 'trusted', 'trusted'])

if __name__ == "__main__":
    unittest.main(exit=False)
    print "Unit Test Passed!"
