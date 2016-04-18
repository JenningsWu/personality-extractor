# -*- coding: utf-8 -*-
#Classify partited data
#sentences description type(desc_type):action(0), speech(1), description(2)
#Character Personality type(personality):[impulsive(1)/calm(0),Extrovert(1)/Introvert(0),
#                                         Optimistic(1)/pessimistic(0)]
import sys
import os
import json
import io
#Data Structures
descTypeProb = dict()   #{word:[probability of 3 desc_type]}
personalityProb = dict()#{word:{desctype:6 probabilities for each personalites},...}
descType = [0,0,0]#action, speech, description
descTypeOutput = -1 #action(0), speech(1), description(2)
personality = [0,0,0,0,0,0]#impulsive,calm, Extrovert, Introvert, Optimistic, pessimistic
personalityOutput = [0,0,0]#[impulsive(1)/calm(0),Extrovert(1)/Introvert(0),Optimistic(1)/pessimistic(0)]

actionCount = 0
speechCount = 0
descriptionCount = 0
totalCount = 0
diffWordCount = 0
modelPath = 'e:/1/k_model.txt'
testDataPath = 'e:/1/k_partition.txt.json'
#load model
modelFile = open(modelPath,'r')
diffWordCount = int(modelFile.readline())
for i in range(0,diffWordCount):
    line = modelFile.readline()
    data = line.strip('\n').split('\t')
    data[0] = data[0].decode('gb2312')
    descTypeProb.setdefault(data[0],[0,0,0])
    for j in range(0,3):
        descTypeProb[data[0]][j] = data[j+1]
while True:
    line = modelFile.readline()
    if line:
        data = line.strip('\n').split('\t')
        data[0] = data[0].decode('gb2312')
        #print data
        personalityProb.setdefault(data[0],{})
        for i in range(0,3):
            personalityProb[data[0]].setdefault(i,[0,0,0,0,0,0])
            for j in range(0,6):
                personalityProb[data[0]][i][j] = data[i*6+j+1]
    else:
        break
modelFile.close()
#load test data
test = io.open(testDataPath,'r',encoding = 'utf-8')
#testData = test.read()
dataSets = json.load(test,encoding = 'utf-8')
test.close() 
#analyze & output:
for dataSet in dataSets:
    personality = [0,0,0,0,0,0]
    for i in dataSet['chars']:
        print 'character:',i
        print '\nsentences:\n'
    for i in dataSet['sentences']:
        sentence = ''
        descType = [0,0,0]
        for j in i['tokens']:
            word = j['word']
            sentence += word
            try:
                for k in range(0,3):
                    descType[k] += float(descTypeProb[word][k])
            except:
                continue
        if descType[0]>descType[1] and descType[0] > descType[2]:
            descTypeOutput = 0
        elif descType[1]>descType[2]:
            descTypeOutput = 1
        else:
            descTypeOutput = 2
        print sentence
        if descTypeOutput == 0:
            print "Description Type: Action"
            actionCount += 1
        elif descTypeOutput == 1:
            print "Description Type: Speech"
            speechCount +=1
        else:
            print "Description Type: Description"
            descriptionCount +=1
        for j in i['tokens']:
            word = j['word']
            try:
                for k in range(0,6):
                   personality[k] += float(personalityProb[word][descTypeOutput][k])

            except:
                continue
    for k in range(0,3):
        if personality[2*k] >personality[2*k+1]:
            personalityOutput[k] = 1
        else:
            personalityOutput[k]=0
    print '\nPersonality:\n'
    if personalityOutput[0] == 1:
        print 'impulsive;'
    else:
        print 'calm;'
    if personalityOutput[1] == 1:
        print 'extrovert;'
    else:
        print 'introvert;'
    if personalityOutput[2] == 1:
        print 'optimistic.'
    else:
        print 'pessimistic.'
totalCount = actionCount + speechCount + descriptionCount
print'\nWriting Style:\n'
print'Action:',actionCount/float(totalCount)
print'Speech:',speechCount/float(totalCount)
print'Description:',descriptionCount/float(totalCount)
