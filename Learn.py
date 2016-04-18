# -*- coding: gb2312 -*-
#Learn from the training data
#Classify partited data
#sentences description type(desc_type):action(0), speech(1), description(2)
#Character Personality type(Personality):[impulsive(1)/calm(0),Extrovert(1)/Introvert(0),
#                                         Optimistic(1)/pessimistic(0)]
import json
import math
#Data Structures
descTypeProb = dict()   #{word:[probability of 3 desc_type]}
personalityProb = dict()#{word:{desctype:6 probabilities for each personalites},...}

wordCount = 0
learnFilePath = 'train/corpus1/k_train.json'
modelFilePath = 'k_model.txt'
#load training data
learnFile = open(learnFilePath,'r')
learnFileText = learnFile.read()
dataSets = json.loads(learnFileText.decode('gb2312'))
learnFile.close()
#training
for dataSet in dataSets:
    personality = dataSet['Personality']
    for i in dataSet['sentences']:
        descType = i['desc_type']
        for j in i['tokens']:
            word = j['word']
            wordCount += 1
            descTypeProb.setdefault(word,[0,0,0])
            descTypeProb[word][descType] += 1
            personalityProb.setdefault(word,{})
            for k in range(0,3):
                personalityProb[word].setdefault(k,[0,0,0,0,0,0])
                for p in range(0,3):
                    if personality[p] == 1:
                        personalityProb[word][k][2*p] += 1
                    else:
                        personalityProb[word][k][2*p+1] += 1
#smoothing & modeling
modelFile = open(modelFilePath,'w')
modelFile.write(str(len(descTypeProb.keys()))+'\n')

for word in descTypeProb.keys():
    modelFile.write(word.encode('gb2312') + '\t')
    for k in range(0,3):
        descTypeProb[word][k] = (descTypeProb[word][k]+1)/float(3*len(descTypeProb.keys())+wordCount)
        modelFile.write(str(math.log(descTypeProb[word][k]))+'\t')
        #print word, descTypeProb[word]
    modelFile.write('\n')

for word in personalityProb.keys():
    modelFile.write(word.encode('gb2312') + '\t')
    for k in range(0,3):
        for p in range(0,6):
            personalityProb[word][k][p] = (personalityProb[word][k][p]+1)/float(18*len(personalityProb.keys())+3*wordCount)
            modelFile.write(str(math.log(personalityProb[word][k][p]))+'\t')
            #print word, personalityProb[word]
    modelFile.write('\n')
modelFile.close()


#    print dataSet.keys()
#print type(dataSet['sentences'])
#print dataSet['sentences'][1]['tokens'][1]['word']
