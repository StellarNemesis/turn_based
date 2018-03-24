#! /usr/bin/env python

import re
import os

# emoji to discord/simplecode
_e2d = {
    '💥': ':boom:',
    '🛡': ':shield:',
    '🚫': ':no_entry_sign:',
    '⚡': ':zap:',
    '🎯': ':dart:',
    '💀': ':skull:',
    '❤': ':heart:',
    '🔷': ':large_blue_diamond:',
    '🏵️': ':rosette:',
    '⚔️': ':crossed_swords:',
}

# discord to emoji
_d2e = {_e2d[i]: i for i in _e2d}

# discord emojis missing in markdown
_md = {}


def _convert(rules, infile, outfile=None):
    """Executes a dictionary of replacement rules on a string or file.
       Arguments:
       rules   - dictionary of replacement rules.
       infile  - input file or string
       outfile - (optional: default None) output filename. If unset return string.
    """
    if os.path.isfile(infile):
        with open(infile, 'r') as f:
            infile = f.read()
    for i in rules:
        infile = re.sub(i, rules[i], infile)
    if outfile is not None:
        with open(outfile, 'w') as f:
            f.write(infile)
        return None
    return infile


def e2d(infile, outfile=None):
    """Converts emojis to discord/shortcode.
           Arguments:
           infile  - input file or string
           outfile - (optional: default None) output filename. If unset return string.
    """
    return _convert(_e2d, infile, outfile)


def d2e(infile, outfile=None):
    """Converts discord/shortcode to emojis.
           Arguments:
           infile  - input file or string
           outfile - (optional: default None) output filename. If unset return string.
    """
    return _convert(_d2e, infile, outfile)


def md(infile, outfile=None):
    """Changes non-markdown discord/shortcode to emojis.
           Arguments:
           infile  - input file or string
           outfile - (optional: default None) output filename. If unset return string.
    """
    return _convert(_md, infile, outfile)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert emojis in a file.')
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', default=None, help='Output file', nargs='?')
    opt = dict(default=False, action="store_true")
    parser.add_argument('-e2d', help='Convert emojis to discord (default)', **opt)
    parser.add_argument('-d2e', help='Convert discord to emoji', **opt)
    parser.add_argument('-md', help='Convert the discord icons not rendered by markdown', **opt)

    args = parser.parse_args()
    if sum([1 for i in [args.e2d, args.d2e, args.md] if i]) > 1:
        raise RuntimeError('Cannot specify more than 1 conversion option.')

    if args.d2e:
        print(d2e(args.infile, args.outfile))
    elif args.md:
        print(md(args.infile, args.outfile))
    else:
        print(e2d(args.infile, args.outfile))
