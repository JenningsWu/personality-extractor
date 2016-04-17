#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import sys
import json
import io

coreNLPLibDir = "c:\\corenlp"
trainDir = os.path.join('train', 'corpus*')
trainTmpDir = os.path.join('train', 'tmp')
curDir = os.path.abspath(sys.path[0])
propertiesPath = os.path.join('properties', 'StanfordCoreNLP-chinese.properties')
nounPos = set(['NN', 'NR', 'PN'])


def concatTokens(tokens):
    return u''.join(map(lambda x: x['word'], tokens))

if __name__ == "__main__":
    trainFiles = glob.glob(os.path.join(trainDir, u"*.txt"))
    for fName in trainFiles:
        # fName = u"train\corpus1\朝闻道.txt"
        tmpFile = os.path.join(trainTmpDir, os.path.basename(fName) + ".json")
        if not os.path.isfile(tmpFile):
            print (tmpFile.encode('utf-8') +
                   " doesn't exist, please run preprocess.py first.")
            continue
        with io.open(tmpFile, 'r') as jsonF, io.open(
            fName,'r', encoding='utf-8') as trainF:
            article = json.load(jsonF, encoding="utf-8")
            i, lineNum, line = 0, 0, trainF.readline()
            j = 0
            while i < len(article['sentences']) and line != '':
                word = article['sentences'][i]['tokens'][j]['word']
                # print line.encode('utf-8')
                index = line.find(word)
                if index > -1:
                    article['sentences'][i]['tokens'][j]['line'] = lineNum
                    line = line[index+len(word):]
                    if line == '':
                        line = trainF.readline()
                        lineNum += 1
                    j += 1
                    if j == len(article['sentences'][i]['tokens']):
                        i += 1
                        j = 0
                else:
                    line = trainF.readline()
                    lineNum += 1
            if i < len(article['sentences']):
                print ("Found some text bugs in " + fName.encode('utf-8') +
                       ", skip it")
                continue

        for sentence in article['sentences']:
            firstFlag = True
            firstNoun = -1
            for token in sentence['tokens']:
                if firstFlag and token['pos'] in nounPos:
                    firstNoun = token['index'] - 1
                    firstFlag = False
            sentence['firstNoun'] = firstNoun

        # break
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
