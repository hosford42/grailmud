cd grailmud
python setup.py bdist_wininst bdist_egg sdist
rmdir build
mv dist ../dist
cd ..
svntagrelease.py
