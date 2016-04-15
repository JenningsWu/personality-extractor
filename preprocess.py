import glob
import os
import sys
from subprocess import call
import argparse

coreNLPLibDir = "c:\\corenlp"
trainDir = 'train/corpus1'
trainTmpDir = 'train/tmp'
curDir = os.path.abspath(sys.path[0])
propertiesPath = "properties/StanfordCoreNLP-chinese.properties"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pre-process training set.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='regenerate existent output files')
    args = parser.parse_args()
    training = glob.glob(os.path.join(trainDir, "*.txt"))
    if args.force:
        fileList = set()
    else:
        existFile = glob.glob(os.path.join(curDir, trainTmpDir, "*.json"))
        fileList = set(map(lambda f: os.path.splitext(os.path.basename(f))[0],
                           existFile))
    for fName in training:
        if os.path.basename(fName) not in fileList:
            call(['java', '-mx4g', '-cp', os.path.join(coreNLPLibDir, '*'),
                  'edu.stanford.nlp.pipeline.StanfordCoreNLP',
                  '-props', os.path.join(curDir, propertiesPath),
                  '-file', os.path.join(curDir, fName),
                  '-outputFormat', 'json',
                  '-outputDirectory', os.path.join(curDir, trainTmpDir)])
