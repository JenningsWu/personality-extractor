# -*- coding: gb2312 -*-
#Classify partited data
#sentences description type(desc_type):action(0), speech(1), description(2)
#Character Personality type(personality):[impulsive(1)/calm(0),Extrovert(1)/Introvert(0),
#                                         Optimistic(1)/pessimistic(0)]
import json
#Data Structures
descTypeProb = dict()   #{word:[probability of 3 desc_type]}
personalityProb = dict()#{word:{desctype:6 probabilities for each personalites},...}
descType = [0,0,0]#action, speech, description
descTypeOutput = -1 #action(0), speech(1), description(2)
personality = [0,0,0,0,0,0]#impulsive,calm, Extrovert, Introvert, Optimistic, pessimistic
personalityOutput = [0,0,0]#[impulsive(1)/calm(0),Extrovert(1)/Introvert(0),Optimistic(1)/pessimistic(0)]

diffWordCount = 0
modelPath = 'k_model.txt'
testDataPath = 'train/partition/k_partition.txt.json'
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
test = open(testDataPath,'r')
testData = test.read()
dataSets = json.loads(testData.decode('gb2312'))
test.close() 
#analyze & output:
for dataSet in dataSets:
    personality = [0,0,0,0,0,0]
    for i in dataSet['chars']:
        print 'character:',i
    for i in dataSet['sentences']:
        descType = [0,0,0]
        for j in i['tokens']:
            word = j['word']
            #print descTypeProb[word][0]
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
        print descTypeOutput
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
print personalityOutput

