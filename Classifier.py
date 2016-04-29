
# Classify partited data
# sentences description type(desc_type):action(0), speech(1), description(2)
# Character Personality type(personality):
#       [impulsive(1)/calm(0),Extrovert(1)/Introvert(0),
#        Optimistic(1)/pessimistic(0)]
import glob
import json
import io
# Data Structures
# {word:[probability of 3 desc_type]}
descTypeProb = dict()
# {word:{desctype:6 probabilities for each personalites},...}
personalityProb = dict()
descType = [0, 0, 0]  # action, speech, description
descTypeOutput = -1  # action(0), speech(1), description(2)
# impulsive,calm, Extrovert, Introvert, Optimistic, pessimistic
personality = [0, 0, 0, 0, 0, 0]
# [impulsive(1)/calm(0),Extrovert(1)/Introvert(0),Optimistic(1)/pessimistic(0)]
personalityOutput = [0, 0, 0]

actionCount = 0
speechCount = 0
descriptionCount = 0
totalCount = 0
diffWordCount = 0
sentenceTypePrior = [0,0,0]#[0]:quote [1]: normal [2]:half
personalityPrior = [0,0,0,0,0,0]
tagFiles = 'train/developing data/'
modelPath = 'model.txt'
testDataFiles = 'train/developing data/*.json'
#variables for experiment
totalDescType = [0,0,0]#speech,description,action
speech = [0,0]#correct,wrong
description = [0,0]
action = [0,0]

totalPersonality = [0,0,0,0,0,0]
impulsive = [0,0]
calm = [0,0]
extrovert = [0,0]
introvert = [0,0]
optimistic = [0,0]
pessimistic = [0,0]


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

# load model
modelFile = open(modelPath, 'r')
sentenceTypePrior = modelFile.readline().split()
for i in range (0,3):
    descType[i] = float(sentenceTypePrior[i])
personalityPrior = modelFile.readline().split()
for i in range(0,6):
    personality[i] = float(personalityPrior[i])
diffWordCount = int(modelFile.readline())
for i in range(0, diffWordCount):
    line = modelFile.readline()
    data = line.strip('\n').split('\t')
    data[0] = data[0].decode('utf-8')
    descTypeProb.setdefault(data[0], [0,0,0])
    for j in range(0, 3):
        descTypeProb[data[0]][j] = data[j + 1]

while True:
    line = modelFile.readline()
    if line:
        data = line.strip('\n').split('\t')
        data[0] = data[0].decode('utf-8')
        # print data
        personalityProb.setdefault(data[0], {})
        for i in range(0, 3):
            personalityProb[data[0]].setdefault(i, [0, 0, 0, 0, 0, 0])
            for j in range(0, 6):
                personalityProb[data[0]][i][j] = data[i * 6 + j + 1]
    else:
        break
modelFile.close()
# load test data
testDataPath = glob.glob(testDataFiles)
for t in testDataPath:
    test = open(t, 'r')
    t = t.decode('gb2312')
    #print t
    novelName = t[10:len(t)-9]
    #print novelName
    tagPath = tagFiles + novelName + '.tag'
    tagDict = parseTagFile(tagPath)
    dataSets = json.load(test, encoding='utf-8')
    test.close()
    print 'Novel Name: ', novelName.encode('gb2312')
    print '\n'
# analyze & output:
    for dataSet in dataSets:
        personality = [0, 0, 0, 0, 0, 0]
        cname = ''
        for name in tagDict.keys():
            if name not in dataSet['chars']:
                continue
            else:
                cname = name
        if cname == '':
            continue
        else:
            #print 1
            for i in range (0,3):
                if tagDict[cname][i]==1:
                    totalPersonality[2*i]+=1
                else:
                    totalPersonality[2*i+1]+=1
            
            print 'Character:', cname.encode('gb2312')
            print 'Aliases:\n'
            for i in dataSet['chars']:
                print i.encode('gb2312'),'\t'
            print '\nsentences:\n'
            for i in dataSet['sentences']:
                sentence = ''
                typeTag = i['type']
                #typeTag ==0:speech
                if typeTag == 1 :
                    typeTag = 2#action
                elif typeTag ==3:
                    typeTag = 1#description
                totalDescType[typeTag]+=1
                descType = [0,0,0]
                for j in i['tokens']:
                    word = j['word']
                    sentence += word
                    try:
                        for k in range(0, 3):
                            #print descTypeProb[word][k]
                            descType[k] += float(descTypeProb[word][k])
                    except:
                        continue
                #print descType
                if descType[0] > descType[1] and descType[0] > descType[2]:
                    descTypeOutput = 0
                elif descType[1]>descType[0] and descType[1] > descType[2]:
                    descTypeOutput = 1
                else:
                    descTypeOutput = 2
                print sentence.encode('utf-8')
                #print typeTag
                if descTypeOutput == 0:
                    print "Description Type: Speech"
                    speechCount += 1
                    if typeTag == descTypeOutput:
                        speech[0]+=1
                    else:
                        speech[1]+=1               
                elif descTypeOutput == 1:
                    print "Description Type: Description"
                    descriptionCount += 1
                    if typeTag == descTypeOutput:
                        description[0]+=1
                    else:
                        description[1]+=1 
                else:
                    print "Description Type: Action"
                    actionCount += 1
                    if typeTag == descTypeOutput:
                        action[0]+=1
                    else:
                        action[1]+=1 
                for j in i['tokens']:
                    word = j['word']
                    try:
                        for k in range(0, 6):
                            personality[k] += float(
                                personalityProb[word][descTypeOutput][k])
                    except:
                        continue
            for k in range(0, 3):
                if personality[2 * k] > personality[2 * k + 1]:
                    personalityOutput[k] = 1
                else:
                    personalityOutput[k] = 0
            print '\nPersonality:\n'
            if personalityOutput[0] == 1:
                print 'impulsive;'
                if tagDict[cname][0] == 1:
                    impulsive[0]+=1
                else:
                    impulsive[1]+=1
            else:
                print 'calm;'
                if tagDict[cname][0] == 0:
                    calm[0]+=1
                else:
                    calm[1]+=1
            if personalityOutput[1] == 1:
                print 'extrovert;'
                if tagDict[cname][1] == 1:
                    extrovert[0]+=1
                else:
                    extrovert[1]+=1
            else:
                print 'introvert;'
                if tagDict[cname][1] == 0:
                    introvert[0]+=1
                else:
                    introvert[1]+=1
            if personalityOutput[2] == 1:
                print 'optimistic.'
                if tagDict[cname][2] == 1:
                    optimistic[0]+=1
                else:
                    optimistic[1]+=1
            else:
                print 'pessimistic.'
                if tagDict[cname][2] == 0:
                    pessimistic[0]+=1
                else:
                    pessimistic[1]+=1
            print '\n'
    totalCount = actionCount + speechCount + descriptionCount
    print'\nWriting Style:\n'
    print'Speech:', speechCount / float(totalCount)
    print'Action:', actionCount / float(totalCount)
    print'Description:', descriptionCount / float(totalCount)
print  totalDescType,speech,description,action
print totalPersonality,impulsive,calm,extrovert,introvert,optimistic,pessimistic
