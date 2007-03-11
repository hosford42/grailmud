import re
import subprocess

instring = open('grailmud/grailmud.egg-info/PKG-INFO').read()

ver = re.search("^Version\:\s*(.*)$", instring, re.MULTILINE).group(1)

subprocess.call('svn copy . https://grailmud.googlecode.com/svn/tags/'
                'release-%(v)s -m "Tagging version %(v)s"' % {'v': ver})
