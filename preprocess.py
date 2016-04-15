import glob
import os
import sys
from subprocess import call

coreNLPLibDir = "c:\\corenlp"
trainDir = 'train/corpus1'
trainTmpDir = 'train/tmp'
curDir = os.path.abspath(sys.path[0])
propertiesPath = "properties/StanfordCoreNLP-chinese.properties"

if __name__ == "__main__":
    training = glob.glob(os.path.join(trainDir, "*.txt"))
    for fName in training:
        call(['java', '-mx4g', '-cp', os.path.join(coreNLPLibDir, '*'),
              'edu.stanford.nlp.pipeline.StanfordCoreNLP',
              '-props', os.path.join(curDir, propertiesPath),
              '-file', os.path.join(curDir, fName),
              '-outputFormat', 'json',
              '-outputDirectory', os.path.join(curDir, trainTmpDir)])
