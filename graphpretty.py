import re
import itertools

non_qualified_name = re.compile('\"(?=(?!grailmud| ))')

notouch_lines_in = 4


def postprocess(infile, outfile):
    lineiter = iter(infile)
    for _ in xrange(notouch_lines_in):
        outfile.write(lineiter.next())
    seen = set()
    for line in lineiter:
        qualified = re.sub(non_qualified_name, '"grailmud.', line)
        if qualified not in seen:
            outfile.write(qualified)
            seen.add(qualified)


if __name__ == '__main__':
    infile = open('pylintintimports')
    outfile = open('_pylintintimports', 'w')
    outstring = postprocess(infile, outfile)
    infile.close()
    outfile.close()
