from questionbox import *
import re
def importText(textfile):
    with open(textfile) as thequestions:
        examString = thequestions.read()
    return examString

def splitclean(listWithLabels):
    # utility function to chop up list of [label, item, label, item]
    if listWithLabels[0] == '':
        del(listWithLabels[0])
    cleanlist = []
    for count in range(len(listWithLabels)):
        if count % 2 == 0:
            cleanlist.append((listWithLabels[count], listWithLabels[count + 1]))
    return cleanlist

def splitIntoBlocks(examString):
    blocks = re.split('(^BLOCK[1-9]*)|(NOBLOCK)', examString, flags=re.M)
    blocks = [item for item in blocks if item is not None]
    return splitclean(blocks)

def splitIntoQuestions(blocktuple):
    questions = re.split('(QUESTION[1-9]*)', blocktuple[1].strip(), flags=re.M)
    if blocktuple[0].strip() != 'NOBLOCK':
        header = questions.pop(0).strip()
        blockid = blocktuple[0].strip()
    else:
        header = None
        blockid = None
    return {'blockid': blockid, 'header': header, 'questions': splitclean(questions)}

def makeBlocks(textBlocks, exam):
    for block in textBlocks:
        if block['blockid'] != None:
            exam.addBlock(QBlock(block['blockid'], block['header']))

def makeQ(questiontupe, blockID):
    QID = questiontupe[0]
    qbust = re.split('ANSWERS', questiontupe[1])
    QPROMPT = qbust[0].strip()
    ansbust = re.split('EXPLAIN', qbust[1])
    explbust = re.split('SUBJECTS', ansbust[1])
    EXPLANATION = explbust[0].strip()
    SUBJECTS = explbust[1].splitlines()
    SUBJECTS = [i.strip() for i in SUBJECTS if i != '']
    anslista = re.split('^(\*?[A-Za-z1-9]\.)', ansbust[0], flags=re.M)
    anslistb = [i.strip() for i in anslista]
    anslist = splitclean(anslistb)
    ANSWERS = OrderedDict()
    for eachtupe in anslist:
        if eachtupe[0].strip()[0] is '*':
            newname = eachtupe[0][1:].strip()
            ANSWERS[newname] = eachtupe[1].strip()
            CORRECT = newname
        else:
            ANSWERS[eachtupe[0]] = eachtupe[1].strip()
    if blockID == 'NOBLOCK':
        BID = None
    else:
        BID = blockID
    return Question(BID, QID, QPROMPT, ANSWERS, CORRECT, EXPLANATION, SUBJECTS)

def parseText(examTextFile):
    holderExam = Exam()
    examString = importText(examTextFile)
    blocktuples = splitIntoBlocks(examString)
    parsedBlocks = [splitIntoQuestions(i) for i in blocktuples]
    makeBlocks(parsedBlocks, holderExam)
    for bt in parsedBlocks:
        for aq in bt['questions']:
            holderExam.addQuestion(makeQ(aq, bt['blockid']))
    return holderExam
