from glob import glob
import os
import re

titlepattern = re.compile("=+\n(.+)\n=+")
linktemplate = '<a href="%s">%s</a>'
codepattern = re.compile('``(.+)``')
def codetemplate(match):
    return '<tt class="docutils literal"><span class="pre">%s</span></tt>' %\
           match.group(1)

filenames = [name[:-4] for name in glob('*.rst')]

linkies = []

for filename in filenames:
    contents = open(filename + '.rst').read()
    match = titlepattern.search(contents)
    title = re.sub(codepattern, codetemplate, match.group(1))
    htmlname = filename + '.html'
    linkies.append(linktemplate % (htmlname, title))

template = open('template-template.txt').read()
open("template.txt", 'w').write(template % '\n<br />\n'.join(linkies))

for filename in filenames:
    calling = "rst2html.py --template template.txt %s.rst > %s.html" % \
              (filename, filename)
    os.popen(calling)
