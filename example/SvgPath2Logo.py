#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os

class SvgPath2Logo:


    #Interpreters
    MSWLOGO = 'mswlogo'
    XLOGO = 'xlogo'

    def _chunks(self, l, size):
        for i in xrange(0, len(l), size):
            yield l[i:i+size]


    def _translate(self, cmd, args, scale=1):

        translation = {
            'm': ('relative_moveto', scale, -scale),
            'M': ('absolute_moveto', scale, -scale),
            'z': ('closepath', ),
            'Z': ('closepath', ),
            'l': ('relative_lineto', scale, -scale),
            'L': ('absolute_lineto', scale, -scale),
            'h': ('relative_horizontal_lineto', scale),
            'H': ('absolute_horizontal_lineto', scale),
            'v': ('relative_vertical_lineto', -scale),
            'V': ('absolute_vertical_lineto', -scale),
            'c': ('relative_cubic_bezier', scale, -scale, scale, -scale, scale, -scale),
            'C': ('absolute_cubic_bezier', scale, -scale, scale, -scale, scale, -scale),
            's': ('relative_smooth_cubic_bezier', scale, -scale, scale, -scale),
            'S': ('absolute_smooth_cubic_bezier', scale, -scale, scale, -scale),
            'q': ('relative_quadratic_bezier', scale, -scale, scale, -scale),
            'Q': ('absolute_quadratic_bezier', scale, -scale, scale, -scale),
            't': ('relative_smooth_quadratic_bezier', scale, -scale),
            'T': ('absolute_smooth_quadratic_bezier', scale, -scale),
            'a': ('relative_arc', scale, scale, -1, 1, 1, scale, -scale),
            'A': ('absolute_arc', scale, scale, -1, 1, 1, scale, -scale),
        }

        coef = translation[cmd][1:]
        args = [str(float(args[i])*coef[i]) for i in range(len(coef))]

        return ('%s %s' % (translation[cmd][0], ' '.join(args))).strip()


    def _commands(self, path):
        pathre = re.compile('([mzlhvcsqta])([^mzlhvcsqta]*)', flags=re.I)
        argsre = re.compile('[\+\-]?[^\-\+\s\t\n\r,$]+')

        for cmd, args in pathre.findall(path):

            args = argsre.findall(args)

            if cmd.lower()=='m':
                for c in self._chunks(args, 2):
                    yield (cmd, c)
                    cmd = 'l' if cmd in 'ml' else 'L'
                    
            elif cmd.lower()=='z':
                yield (cmd, [])

            else:
                size = {
                    'h':1, 'H':1, 'v':1, 'V':1,
                    'l':2, 'L':2, 't':2, 'T':2,
                    's':4, 'S':4, 'q':4, 'Q':4,
                    'c':6, 'C':6,
                    'a':7, 'A':7,
                }

                for c in self._chunks(args, size[cmd]):
                    yield (cmd, c)


    def toLogo(self, path, interpreter=XLOGO, scale=1):
        """Converts svg path to logo commands.
        @param path: is svg path
        @type path: str|unicode
        @param interpreter: logo interpreter. It can be SvgPath2Logo.MSWLOGO
        or SvgPath2Logo.XLOGO for other interpreters as 
        "http://www.calormen.com/jslogo/" or "https://turtleacademy.com" 
        @param scale: it is used to enlarge or shrink the graph
        @type scale: int|float
        @return: logo commands
        @rtype: str
        """


        #include logo lib
        lib = os.path.join(os.path.dirname(__file__), 'lib', '%s.lgo' % interpreter)
        out = open(lib, 'rb').read()

        #add logo commands
        for cmd, args in self._commands(path):
            out += self._translate(cmd, args, scale) + '\n'

        return out
