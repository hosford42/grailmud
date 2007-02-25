import subprocess

subprocess.call("python grailmud/setup.py sdist -d ./dist")
subprocess.call("python grailmud/setup.py bdist --format=wininst -d ./dist")
