from collections import OrderedDict
import warnings
import re

class Question(object):
    """A single question with a unique correct answer.
    Attributes:
        block: string or None; string if this question belongs to block of
            questions, where the string is unique identifier for that block.
        qid: string, unique question identifier
        prompt: string, question prompt
        answers: ordered dict of {string, string} where first string is answer
            ID as number/letter and second string is answer text.
        correct: string, representing correct answerID
        explanation: string containing explanation of correct answer.
        subjects: list of strings representing topics (for competency analysis)
    """
    def __init__(self, BLOCK, QID, PROMPT, ANSWERS, CORRECT, EXPLANATION, SUBJECTS):
        self.qid = QID
        self.prompt = PROMPT
        self.answers = ANSWERS
        self.correct = CORRECT
        self.explanation = EXPLANATION
        self.subjects = SUBJECTS
        if not BLOCK:
            self.block = None
        else:
            self.block = BLOCK

    def ask(self):
        return {'block': self.block, 'qid': self.qid, 'prompt': self.prompt, 'answers': self.answers}

    def ans(self):
        return {'block': self.block, 'qid': self.qid, 'prompt': self.prompt, 'answers': self.answers, 'correct': self.correct, 'explanation': self.explanation, "subjects": self.subjects}

    def grade(self, studAns):
        tempans = self.ans()
        if studAns == self.correct:
            tempans['gotRight'] = True
        else:
            tempans['gotRight'] = False
        return tempans

    def HTML(self, aForm = False):
        anslist = []
        for key in sorted(self.answers.keys()):
            if aForm:
                formstring = '<input type = "radio" name = "%s" value = "%s">' % (self.qid, key)
                anslist.append(formstring)
            anslist.append(key)
            anslist.append(self.answers[key])
            anslist.append('<br>')
        del anslist[-1]
        ansstring = ' '.join(anslist)
        derprompt = re.sub('\n', '<br>', self.prompt)
        thestring = '<p><li>%s</p><p>%s</li></p>' % (derprompt, ansstring)
        return thestring

    def answerReport(self, finalanswers):
        anslist = []
        for key in sorted(self.answers.keys()):
            anslist.append(key)
            anslist.append(self.answers[key])
            anslist.append('<br>')
        del anslist[-1]
        ansstring = ' '.join(anslist)
        derprompt = re.sub('\n', '<br>', self.prompt)
        thestring = '<p>%s</p><p>%s</p>' % (derprompt, ansstring)
        evalstring = '<p><b>You left the question blank!</b></p><p><b>Correct answer:</b> %s</p><p><b>Explanation: </b>%s</p>' % (self.answers[self.correct], self.explanation)
        if self.qid in finalanswers:
            if finalanswers[self.qid]:
                answer = finalanswers[self.qid]
                evalstring = '<p><b>You answered:</b> %s</p><p><b>Correct answer:</b> %s</p><p><b>Explanation: </b>%s</p>' % (self.answers[answer], self.answers[self.correct], self.explanation)
        return thestring + evalstring



    def getBlock(self):
        return self.block

    def getID(self):
        return self.qid

    def dictRepr(self):
        return {"block": self.block, "qid": self.qid, "prompt": self.prompt, "answers": self.answers, "correctans": self.correct, "explanation": self.explanation, "subjects": self.subjects}

class QBlock(object):
    """A qBlock is a block of questions, where each block has header text (like
        a prompt that applies to all questions) and question objects within it.
        Example: 'for questions 1-5, assume the following is true... '
        Attributes are header text, list of questions, and blockid.
        blockid must match blockid attribute of question that belongs in block.
    """

    def __init__(self, BLOCKID, HEADER):
        self.blockid = BLOCKID
        self.header =  HEADER
        self.questions = []

    def ask(self):
        qsToAsk = [aQuestion.ask() for aQuestion in self.questions]
        return {'header': self.header, 'questions': qsToAsk}

    def HTML(self, aForm = False):
        if aForm:
            questionstring = '<br>'.join([question.HTML(aForm = True) for question in self.questions])
        else:
            questionstring = '<br>'.join([question.HTML() for question in self.questions])
        derheader = re.sub('\n', '<br>', self.header)
        fullstring = '<p>%s</p>%s' % (derheader, questionstring)
        return fullstring

    def answerReport(self, finalanswers):
        questionstring = '<br>'.join([question.answerReport(finalanswers) for question in self.questions])
        derheader = re.sub('\n', '<br>', self.header)
        fullstring = '<p>%s</p>%s' % (derheader, questionstring)
        return fullstring

    def addQuestion(self, aQuestion):
        if type(aQuestion) is not Question:
            raise TypeError
        self.questions.append(aQuestion)

    def getHeader(self):
        return self.header

    def getID(self):
        return self.blockid

    def getQuestions(self):
        return self.questions

    def dictRepr(self):
        return {'blockid': self.blockid, 'blockheader': self.header}


class NoneBlock(QBlock):
    """Special qBlock for standalone questions (that don't have an assigned
    block in the underlying data file)
    """
    def __init__(self):
        self.blockid = 0
        self.header = None
        self.questions = []

class Exam(object):
    def __init__(self):
        self.blocks = OrderedDict()
        self.questions = OrderedDict()
        self.grades = []

    def getQIDs(self):
        return [self.questions[ques].qid for ques in self.questions]

    def getSubjects(self):
        messlist = [self.questions[ques].subjects for ques in self.questions]
        def flatten(l):
            out = []
            for item in l:
                if item:
                    if isinstance(item, (list, tuple)):
                        out.extend(flatten(item))
                    else:
                        out.append(item)
            return out
        return list(set(flatten(messlist)))

    def subjectCounts(self):
        subjcounts = {}
        for subject in self.getSubjects():
            for ques in self.questions:
                if subject in self.questions[ques].subjects:
                    if subject in subjcounts:
                        subjcounts[subject] += 1
                    else:
                        subjcounts[subject] = 1
        return subjcounts


    def HTML(self, aForm = False, CGIurl = None):
        if aForm:
            if not CGIurl:
                warnings.warn('Expected a script url when producing an HTML form.')
            basestring = '<hr>'.join([self.blocks[block].HTML(aForm = True) for block in self.blocks])
            newstring = '<form action="%s" method="post"><ol>%s</ol><br><center><button type="submit">Submit</button></center></form>' % (CGIurl, basestring)
            return newstring
        return '<hr>'.join([self.blocks[block].HTML() for block in self.blocks])

    def answerReport(self, finalanswers):
        return '<hr>'.join([self.blocks[block].answerReport(finalanswers) for block in self.blocks])


    def assignBlock(self, aQuestion):
        # aQuestion is a question object.  dumps q in noneblock if its designated block does not exist.
        if aQuestion.getBlock() and (aQuestion.getBlock() in self.blocks):
            self.blocks[aQuestion.getBlock()].addQuestion(aQuestion)
        else:
            if 0 not in self.blocks:
                self.blocks[0] = NoneBlock()
            self.blocks[0].addQuestion(aQuestion)

    def addBlock(self, aBlock):
        # aBlock is a block object.
        self.blocks[aBlock.getID()] = aBlock

    def addQuestion(self, aQuestion):
        self.questions[aQuestion.getID()] = aQuestion
        self.assignBlock(aQuestion)

    def load(self, jsonfile):
        from json import load as jload
        with open(jsonfile) as thejson:
            qdict = jload(thejson)
        for biter in qdict['blocks']:
            btemp = QBlock(biter['blockid'], biter['blockheader'])
            self.addBlock(btemp)
        for qiter in qdict['questions']:
            qtemp = Question(qiter['block'], qiter['qid'], qiter['prompt'], qiter['answers'], qiter['correctans'], qiter['explanation'], qiter['subjects'])
            self.addQuestion(qtemp)

    def administer(self):
        return [eachblock.ask() for eachblock in self.blocks.values()]

    def grade(self, answers):
        # answers is a list of (qid, student answer) pairs as tupe of strings
        for answer in answers:
            self.grades.append(self.questions[answer[0]].grade(answer[1]))
        return self.grades

    def save(self, jsonfile = None):
        outdict = {}
        outdict['blocks'] = [eachblock.dictRepr() for eachblock in self.blocks.values() if eachblock.getID() != 0]
        outdict['questions'] = [eachq.dictRepr() for eachq in self.questions.values()]
        if jsonfile:
            from json import dump as jdump
            with open(jsonfile, 'w') as outfile:
                jdump(outdict, outfile, indent=4)
        return outdict
