#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import json
import io

trainDir = os.path.join('train', 'corpus*')
trainTmpDir = os.path.join('train', 'tmp')
outDir = os.path.join('train', 'partition')


if __name__ == "__main__":
    trainFiles = glob.glob(os.path.join(trainDir, u"*.txt"))
    with io.open(u'train/partition/孔乙己.txt.json', 'r', encoding='utf-8') as f:
        j = json.load(f, encoding="utf-8")
        out = []
        for c in j:
            if u"孔乙己" in c['chars']:
                out.append(c)
                print 'found'
        outFile = os.path.join(outDir, "k_partition.txt.json")
        with io.open(outFile, 'w', encoding='utf-8') as outf:
            outf.write(unicode(json.dumps(out, ensure_ascii=False)))
