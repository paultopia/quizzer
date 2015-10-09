Work in progress.

Experimental application to render exam questions grabed from a plaintext list or json and store in json. Usage: use the parser to process a text file in similar form as the example, where asterisk indicates correct answer and multiple carriage returns for spacing are ignored. Produces exam object which can then be saved into json and which, when project is done, will be able to be administered as pure python cgi, scored programmatically, save results to an appropriate datatype, and display individual results to student.  

Requires python 2.7.

questionbox.py is core functionality.  

parsetext.py parses text files formated like qstest.txt (and if saved using the save.() method of questionbox.Exam, produces output like testtest.json)

makeweb.py produces an index.html file suitable for upload to the web to serve a quiz.  that quiz points to a CGI file that handles evaluation and reporting.  This ought to simply spit out the html on the fly as a cgi script on its own that students can directly access, but when implementing this myself, I learned that the webserver I'm on doesn't play nice with python 2.7 features, so implementing this will have to wait.

process.py is meant to be run as cgi, and to catch the output from the html produced by makeweb.py.  
