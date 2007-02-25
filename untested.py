import os

def main(directory):
    for rawfilename in os.listdir(directory):
        if rawfilename not in ('.svn', 'test'):
            filename = os.path.join(directory, rawfilename)
            if os.path.isdir(filename):
                main(filename)
            elif filename.endswith('.py'):
                if not os.access(os.path.join(directory, 'test', 
                                              'test_%s' % rawfilename), 
                                 os.F_OK):
                    if rawfilename not in ['__init__.py']:
                        print '%s not tested!' % filename

if __name__ == '__main__':
    main(os.path.join(os.curdir, 'grailmud'))

