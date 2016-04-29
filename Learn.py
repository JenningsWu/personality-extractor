# -*- coding: gb2312 -*-
# Learn from the training data
# Classify partited data
# sentences description type(desc_type):action(0), speech(1), description(2)
# Character Personality type(Personality):
#           [impulsive(1)/calm(0),Extrovert(1)/Introvert(0),
#            Optimistic(1)/pessimistic(0)]
import json
import math
import glob
# Data Structures
descTypeProb = dict()  # {word:[probability of 3 desc_type]}
# {word:{desctype:6 probabilities for each personalites},...}
personalityProb = dict()
sentenceTypePrior = [0,0,0]#[0]:quote [1]: normal [2]:half
personalityPrior = [0,0,0,0,0,0]
wordCount = 0
characterCount = 0
tagFiles = 'train/classifier training data/'
partitionFiles = 'train/classifier training data/*.json'
modelFilePath = 'model.txt'
count0 = 0
count1=0
count2 = 0
# parsing tag data
def parseTagFile(path):
    tagFile = open(tagPath,'r')
    tagDict = dict()
    while True:
        line = tagFile.readline()
        if line:
            charName = line.strip('\n').decode('utf-8')
            #print charName
            line = tagFile.readline()
            tags = line.strip('\n').split()
            if tags[0] == '\xe5\x86\xb2\xe5\x8a\xa8': # Impulsive
                tags[0] = 1;
            else:
                tags[0] = 0
            if tags[1] == '\xe5\xa4\x96\xe5\x90\x91': # Extrovert
                tags[1] = 1;
            else:
                tags[1] = 0
            if tags[2] == '\xe4\xb9\x90\xe8\xa7\x82': # Optimistic
                tags[2] = 1;
            else:
                tags[2] = 0
            #print tags
            tagDict.setdefault(charName,[])
            tagDict[charName] = tags
            #print tagDict
        else:
            break
    tagFile.close()
    return tagDict

# load training data
partitionPath = glob.glob(partitionFiles)
for p in partitionPath:
    learnFile = open(p, 'r')
    novelName = p[15:len(p)-9]
    tagPath = tagFiles + novelName + '.tag'
    tagDict = parseTagFile(tagPath)
    learnFileText = learnFile.read()
    dataSets = json.loads(learnFileText.decode('utf-8'))
    learnFile.close()
# training
    for dataSet in dataSets:
        cname = ''
        for name in tagDict.keys():
            if name not in dataSet['chars']:
                continue
            else:
                cname = name
                print name
                characterCount +=1
                for i in range(0,3):
                    if tagDict[cname][i]==1:
                        personalityPrior[2*i]+=1
        #personality = dataSet['Personality']
        for i in dataSet['sentences']:
            descType = i['type']
            if i['type'] == 0:
                count0 += 1
            if descType == 0:
                descType = 0 #quote
                sentenceTypePrior[0] += 1
            elif descType == 3:
                descType = 1 #normal
                sentenceTypePrior[1] += 1
            else:
                sentenceTypePrior[2] += 1#half
                descType = 2
            if descType == 1:
                count1 +=1
            if descType ==2:
                count2 +=1
            for j in i['tokens']:
                word = j['word']
                wordCount += 1
                descTypeProb.setdefault(word, [0, 0,0])
                descTypeProb[word][descType] += 1
                if cname != '':
                    personalityProb.setdefault(word, {})
                    for k in range(0, 3):
                        personalityProb[word].setdefault(k, [0, 0, 0, 0, 0, 0])
                    for i in range(0, 3):
                        if tagDict[cname][i] == 1:
                            personalityProb[word][descType][2 * i] += 1
                        else:
                            personalityProb[word][descType][2 * i + 1] += 1
# smoothing & modeling
    #priors
print count0,count1,count2
c0 = sentenceTypePrior[0]
c1 = sentenceTypePrior[1]
c2 = sentenceTypePrior[2]
characterCount += 8 #smoothing
sentenceTypePrior[0] = math.log((c0+1)/float(c0+c1+c2+3))
sentenceTypePrior[1] = math.log((c1+1)/float(c0+c1+c2+3))
sentenceTypePrior[2] = math.log((c2+1)/float(c0+c1+c2+3))
personalityPrior[1] = math.log((characterCount-personalityPrior[0]-4)/\
                               float(characterCount))
personalityPrior[0] = math.log((personalityPrior[0]+4)/\
                               float(characterCount))
personalityPrior[3] = math.log((characterCount-personalityPrior[2]-4)/\
                               float(characterCount))
personalityPrior[2] = math.log((personalityPrior[2]+4)/\
                               float(characterCount))
personalityPrior[5] = math.log((characterCount-personalityPrior[4]-4)/\
                               float(characterCount))
personalityPrior[4] = math.log((personalityPrior[4]+4)/\
                               float(characterCount))

modelFile = open(modelFilePath, 'w')
for i in range (0,3):
    modelFile.write(str(sentenceTypePrior[i])+ '\t')
modelFile.write('\n')
for i in range (0,6):
    modelFile.write(str(personalityPrior[i])+ '\t')
modelFile.write('\n')
modelFile.write(str(len(descTypeProb.keys())) + '\n')

for word in descTypeProb.keys():
    modelFile.write(word.encode('utf-8') + '\t')
    for k in range(0, 3):
        descTypeProb[word][k] = (descTypeProb[word][k] + 1) / \
            float(3 * len(descTypeProb.keys()) + wordCount)
        descTypeProb[word][0] *=2
        descTypeProb[word][1] /=2
        #descTypeProb[word][2] *=2  
        modelFile.write(str(math.log(descTypeProb[word][k])) + '\t')
        # print word, descTypeProb[word]
    modelFile.write('\n')

for word in personalityProb.keys():
    modelFile.write(word.encode('utf-8') + '\t')
    for k in range(0, 3):
        for p in range(0, 6):
            personalityProb[word][k][p] = (personalityProb[word][k][p] + 1) / \
                float(18 * len(personalityProb.keys()) + 3 * wordCount)
            modelFile.write(str(math.log(personalityProb[word][k][p])) + '\t')
            # print word, personalityProb[word]
    modelFile.write('\n')
modelFile.close()


#    print dataSet.keys()
# print type(dataSet['sentences'])
# print dataSet['sentences'][1]['tokens'][1]['word']
