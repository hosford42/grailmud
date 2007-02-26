cd grailmud
python setup.py bdist --formats=wininst,egg -d ../dist
python setup.py sdist -d ../dist
cd ..
