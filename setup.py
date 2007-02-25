__copyright__ = """Copyright 2007 Sam Pointon"""

__licence__ = """
This file is part of grailmud.

grailmud is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

grailmud is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
grailmud (in the file named LICENSE); if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
"""

from setuptools import setup, find_packages
import os

setup(name = "grailmud",
      version = "0.1a0",
      packages = find_packages(),
      package_data = {'grailmud.actiondefs': ['*.py', 'emotefile.txt'],
                      'grailmud': ['LICENSE'],
                      '': ['doc/*', 'test/*']},

#      install_requires = ['durus>=3.6', 'pyparsing', 'twisted',
#                          'functional', 'setuptools'],
      extras_require = {'rest': ['docutils']},

      author = "Sam Pointon",
      author_email = "free.condiments@gmail.com",
      description = "A Python MUD server",
      license = "GNU GPL; see LICENSE",
      keywords = "mud server game mmorpg text adventure",
      url = "http://code.google.com/p/grailmud/",
      classifiers = \
               ["License :: OSI Approved :: GNU General Public License (GPL)",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Topic :: Communications :: Chat",
                "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)"]
)
