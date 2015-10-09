headerpage = 'YOUR HTML FILE PATH HERE'
# headerpage should have instructions, CSS for formatting, etc. -- basically everything other than the
# question form for test-takers to fill out, which is supplied by thequiz.HTML().
questionjson = 'YOUR JSON FILE PATH HERE'
processor = 'YOUR CGI PROCESSOR FILE PATH HERE'
import questionbox
thequiz = questionbox.Exam()
thequiz.load(questionjson)
theForm = thequiz.HTML(True, processor)
with open('headerpage') as topper:
    header = topper.read()
footer = '</body></html>'
page = header + theForm + footer
with open('index.html', 'w') as thepage:
    thepage.write(page)
