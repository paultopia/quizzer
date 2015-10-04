from collections import OrderedDict

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
            qdict = jload(thejson,  object_pairs_hook=OrderedDict)
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
