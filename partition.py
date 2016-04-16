#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import sys
import json
import io

coreNLPLibDir = "c:\\corenlp"
trainDir = 'train/corpus1'
trainTmpDir = 'train/tmp'
curDir = os.path.abspath(sys.path[0])
propertiesPath = "properties/StanfordCoreNLP-chinese.properties"
nounPos = set(['NN', 'NR', 'PN'])

if __name__ == "__main__":
    tmpFiles = glob.glob(os.path.join(trainTmpDir, "*.json"))
    for fName in tmpFiles:
        with io.open(fName, 'r') as f:
            article = json.load(f, encoding="utf-8")
            for sentence in article['sentences']:
                firstFlag = True
                firstNoun = -1
                for token in sentence['tokens']:
                    if firstFlag and token['pos'] in nounPos:
                        firstNoun = token['index'] - 1
                        firstFlag = False
                sentence['firstNoun'] = firstNoun

            # sentences = []
            # for sentence in article['sentences']:
            #     s = {'type': 0, 'tokens': []}
            #     for token in sentence['tokens']:
            #         t = {
            #             'index': token['index'],
            #             'word': token['word'],
            #             'pos': token['pos']}
            #         s['tokens'].append(t)
            #     sentences.append(s)
            # print article['sentences'][1]['firstNoun']
            break

