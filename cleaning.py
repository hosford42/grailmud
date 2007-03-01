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

import os

def get_all_files_from_subdirs(directory):
    for filename in os.listdir(directory):
        if filename != '.svn':
            filename = os.path.join(directory, filename)
            if os.path.isdir(filename):
                for name in get_all_files_from_subdirs(filename):
                    yield name
            else:
                yield filename

def filter_out_trash(files):
    for filename in files:
        #clean out pycs and generated docs
        if filename.endswith('.pyc') or filename.endswith(".html"):
            yield filename

def remove_trash(directory):
    for trashname in filter_out_trash(get_all_files_from_subdirs(directory)):
        print 'Removing %s' % trashname
        os.remove(trashname)

if __name__ == "__main__":
    remove_trash(os.curdir)
