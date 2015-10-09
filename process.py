#!/usr/bin/python

headertext = 'YOUR HEADER TEXT HERE'
# use headertext for everything that goes in your <head> -- javascript, CSS,  whatever.
questionspath 'PATH TO THE JSON WITH YOUR QUESTIONS HERE'
import cgi, cgitb, json
print "Content-Type: text/html\n\n"
print '<html><head><title>Quiz Report</title>'
print headertext
print "</head>"
print '<body><h2>Quiz Report</h2>'
cgitb.enable()
studanswers = cgi.FieldStorage()
finalanswers = {}
for key in studanswers.keys():
    finalanswers[key] = studanswers[key].value
import questionbox
thequiz = questionbox.Exam()
thequiz.load(questionspath)
evaluation = {}
QIDs = thequiz.getQIDs()
for QID in QIDs:
    evaluation[QID] = False
    if QID in finalanswers:
        if finalanswers[QID]:
            evaluation[QID] = thequiz.questions[QID].correct == finalanswers[QID]

answerreport = thequiz.answerReport(finalanswers)
import string
# just to catch ugly non-ascii characters that can crawl in and break things.
newreport = filter(lambda x: x in string.printable, answerreport)
print newreport

subjscores = {}
for QID in QIDs:
    if evaluation[QID] == True:
        for subject in thequiz.questions[QID].subjects:
            if subject in subjscores:
                subjscores[subject] += 1
            else:
                subjscores[subject] = 1
subjlist = thequiz.getSubjects()
subjcounts = thequiz.subjectCounts()

for subject in subjlist:
    if subject not in subjscores:
        subjscores[subject] = 0
ratios = {}
print '<hr><center><b>'
for subject in subjscores:
    print '<p>In %s you got %s right out of %s.</p>' % (subject, subjscores[subject], subjcounts[subject])
    ratios[subject] = float(subjscores[subject]) / float(subjcounts[subject])

loglist = [(evaluation, ratios, finalanswers)]
try:
    with open('logjson.json') as thelog:
        loglist.extend(json.load(thelog))
except:
    pass
with open('logjson.json', 'w') as thelog:
    json.dump(loglist, thelog)

print '<h2>SAVE OR PRINT THIS PAGE IF YOU WANT INDIVIDUAL FEEDBACK.  THESE RESULTS ARE NOT SAVED.</h2></b></center>'
print '</body></html>'
