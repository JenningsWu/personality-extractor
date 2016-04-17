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
outDir = os.path.join('train', 'partition')
curDir = os.path.abspath(sys.path[0])
propertiesPath = os.path.join('properties',
                              'StanfordCoreNLP-chinese.properties')
nounPos = set(['NN', 'NR', 'PN'])
pureNoun = set(['NN', 'NR'])
TOTAL_QUOTE, QUOTE_NORMAL, NORMAL_QUOTE, TOTAL_NORMAL = 0, 1, 2, 3


def concatTokens(tokens):
    return u''.join(map(lambda x: x['word'], tokens))


def extractSentence(sentence):
    s = {'type': sentence['quote'], 'tokens': []}
    for token in sentence['tokens']:
        t = {
            'index': token['index'],
            'word': token['word'],
            'pos': token['pos']}
        s['tokens'].append(t)
    return s

def loadJson(oriFile, tmpFile):
    with io.open(tmpFile, 'r') as jsonF, io.open(
            oriFile, 'r', encoding='utf-8') as trainF:
        article = json.load(jsonF, encoding="utf-8")
        i, lineNum, line = 0, 0, trainF.readline()
        j = 0
        while i < len(article['sentences']) and line != '':
            word = article['sentences'][i]['tokens'][j]['word']
            # print line.encode('utf-8')
            index = line.find(word)
            if index > -1:
                article['sentences'][i]['tokens'][j]['line'] = lineNum
                line = line[index + len(word):]
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
            print ("Found some text bugs in " + oriFile.encode('utf-8') +
                   ", skip it")
            return None
    return article

def assignQuoteFlag(article):
    quoteFlag, lastLineNum = False, 0
    for sentence in article['sentences']:
        if sentence['tokens'][0]['line'] > lastLineNum:
            quoteFlag = False
        s = concatTokens(sentence['tokens'])
        i = s.find(u"“")
        j = s.find(u"”")
        if not quoteFlag:
            if i == 0 or j == 0:
                if j <= 0:
                    sentence['quote'] = TOTAL_QUOTE
                else:
                    sentence['quote'] = QUOTE_NORMAL
            elif i > 0:
                sentence['quote'] = NORMAL_QUOTE
            else:
                sentence['quote'] = TOTAL_NORMAL
        else:
            if i >= 0:
                if i < j or j < 0:
                    sentence['quote'] = QUOTE_NORMAL
                else:
                    sentence['quote'] = TOTAL_NORMAL
            else:
                if j > 0:
                    if j == len(s) - 1:
                        sentence['quote'] = TOTAL_QUOTE
                    else:
                        sentence['quote'] = QUOTE_NORMAL
                else:
                    sentence['quote'] = TOTAL_QUOTE

        if i >= 0 and j < 0:
            quoteFlag = True
        if j == 0:
            quoteFlag = True
        if i < j:
            quoteFlag = False
        if i == len(s) - 1:
            quoteFlag = False
        lastLineNum = sentence['tokens'][
            len(sentence['tokens']) - 1]['line']

    return article

def computeFirstNoun(article):
    for sentence in article['sentences']:
        sentence['firstNoun'] = -1
        if (sentence['quote'] == TOTAL_NORMAL or
                sentence['quote'] == TOTAL_QUOTE):
            for token in sentence['tokens']:
                if token['pos'] in nounPos:
                    sentence['firstNoun'] = token['index'] - 1
                    break
        elif sentence['quote'] == NORMAL_QUOTE:
            for token in sentence['tokens']:
                if token['pos'] in nounPos:
                    sentence['firstNoun'] = token['index'] - 1
                    break
                if token['word'] == u'“' or token['word'] == u'”':
                    break
        else:
            startFlag = False
            for token in sentence['tokens']:
                if startFlag and token['pos'] in nounPos:
                    sentence['firstNoun'] = token['index'] - 1
                    break
                if token['word'] == u'“' or token['word'] == u'”':
                    startFlag = True
    return article

def computeCharMap(article):
    characterMap = {}
    charNumMap = {}
    charNum = 0
    for index, coref in article['corefs'].iteritems():
        allPN = True
        charSet = set()
        for item in coref:
            lineNum = item['sentNum'] - 1
            nounFlag = False
            start = item['startIndex'] - 1
            end = item['endIndex'] - 1
            sentence = article['sentences'][lineNum]
            tokens = sentence['tokens']
            for i in xrange(start, end):
                pos = tokens[i]['pos']
                if pos in pureNoun:
                    nounFlag = True
            allPN = (not nounFlag) and allPN
            word = concatTokens(tokens[start: end])
            charSet.add(word)
            if nounFlag:
                # if characterMap.get(word, charNum) != charNum:
                #     print fName.encode('utf-8')
                #     print "warning!", word.encode('utf-8')
                characterMap[word] = charNum

            firstNoun = article['sentences'][lineNum]['firstNoun']
            if (firstNoun >= start and firstNoun < end and
                    sentence['quote'] == TOTAL_NORMAL):
                article['sentences'][lineNum]['belongTo'] = charNum
        charNumMap[charNum] = {
            'chars': list(charSet),
            'allPN': allPN,
            'sentences': []}
        charNum += 1
    return characterMap, charNumMap

def computeBelongTo(article, characterMap):
    lastSentenceBelongTo = -1
    normal_quote_flag = False
    quoteList = []
    for i, sentence in enumerate(article['sentences']):
        sentence = article['sentences'][i]
        belongTo = sentence.get('belongTo', -1)
        if sentence['quote'] != TOTAL_QUOTE:
            if belongTo < 0 and sentence['firstNoun'] > -1:
                word = sentence['tokens'][sentence['firstNoun']]['word']
                belongTo = characterMap.get(word, -1)
            if sentence['quote'] == TOTAL_NORMAL:
                normal_quote_flag = False
                if len(quoteList) > 0:
                    for index in quoteList:
                        ns = article['sentences'][index]
                        if (sentence['tokens'][0]['line'] ==
                                ns['tokens'][0]['line']):
                            ns['belongTo'] = belongTo
                    quoteList = []
            elif sentence['quote'] == NORMAL_QUOTE:
                normal_quote_flag = True
            elif sentence['quote'] == QUOTE_NORMAL:
                normal_quote_flag = True
                tmpIndex = i - 1
                quoteList = []
                while (tmpIndex >= 0 and
                        article['sentences'][tmpIndex]['quote'] == TOTAL_QUOTE):
                    quoteList.append(tmpIndex)
                    tmpIndex -= 1
                for index in quoteList:
                    article['sentences'][index]['belongTo'] = belongTo
                quoteList = []
        else:
            if normal_quote_flag:
                belongTo = lastSentenceBelongTo
            else:
                quoteList.append(i)
        lastSentenceBelongTo = belongTo
        sentence['belongTo'] = belongTo
    return article

if __name__ == "__main__":
    trainFiles = glob.glob(os.path.join(trainDir, u"*.txt"))
    for fName in trainFiles:
        # fName = u"train\corpus1\斜眼.txt"
        tmpFile = os.path.join(trainTmpDir, os.path.basename(fName) + ".json")
        outFile = os.path.join(outDir, os.path.basename(fName) + ".json")
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        if not os.path.isfile(tmpFile):
            print (tmpFile.encode('utf-8') +
                   " doesn't exist, please run preprocess.py first.")
            continue

        article = loadJson(fName, tmpFile)
        if article is None:
            continue

        article = assignQuoteFlag(article)

        article = computeFirstNoun(article)

        characterMap, charNumMap = computeCharMap(article)

        article = computeBelongTo(article, characterMap)
        

        output = []
        for i, sentence in enumerate(article['sentences']):
            if sentence['belongTo'] > -1:
                charNumMap[sentence['belongTo']]['sentences'].append(
                    extractSentence(sentence))
        for key, item in charNumMap.iteritems():
            if len(item['sentences']) > 0:
                output.append(item)
        with io.open(outFile, 'w', encoding='utf-8') as outf:
            outf.write(unicode(json.dumps(output, ensure_ascii=False)))
