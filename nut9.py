"""
The idea, roughly, is as follows:
- Lines can be expressed as binary strings (i.e. sequences of 1s and 0s).
- The next line is calculated by "sliding" a 5-bit buffer through a line and
  piecing together a new line bit by bit, according to the given rules.
- Since the buffer has 5 bits, it can exist in 2^5 = 32 different states, each
  of which corresponds either to a filled or blank square (1 or 0). Since this
  is determined by fixed rules, the state—result relations need to be calculated
  only once, and can then be accessed from memory.
- Nothing beyond a primitive integer and basic bitwise operations is needed to
  to handle the buffer.
- When calculating lines, two things are kept track of: (1) the patterns of
  filled and blank squares, and (2) their horizontal placement relative to the
  the first line ("offset").
- Each new line is stored in two sets: one which considers both the pattern and
  and its offset, and another which considers only the pattern. Checking the
  the membership of a new line in these sets is key in distinguishing "blinking"
  vs. "gliding" patterns.
"""

from timeit import default_timer as clock



def calculateStates():
    states = {}

    for i in range(32):
        binary = format(i, '05b')
        filled = sum([ 1 for bit in binary if bit == '1' ])

        if binary[2] == '0':
            states[i] = filled == 2 or filled == 3
        else:
            states[i] = filled == 3 or filled == 5

    return states



class Pattern(object):
    """
    A pattern of filled and blank squares is expressed as a list of integers,
    indicating run lengths. For example, the sequence ##....#####...# translates
    to [ 2, 4, 5, 3, 1 ].

    Because blank squares on either end are meaningless, the first and last list
    entries always stand for filled squares. That is, runs of filled squares are
    found in even, and blank squares in odd indexes.

    In addition to the pattern itself, also its offset (distance of the leading
    filled square relative to the initial line) is memorized.
    """
    def __init__(self, offset = 0):
        self.runs = []
        self.offset = offset
        self.count = 0

    def insert(self, bit, steps = 1):
        if not self.runs and not self.count and not bit:  # Disregards blanks
            return                                        # at beginning.

        filled = len(self.runs) % 2 == 0
        if (filled and not bit) or (not filled and bit):
            self.runs.append(self.count)
            self.count = 0

        self.count += steps

    def complete(self):
        if len(self.runs) % 2 == 0:       # Append the "hanging" run of filled
            self.runs.append(self.count)  # squares, if any.
            self.count = 0

        return self



def read(pattern, states):
    bit = 1
    buffer = 0
    p = Pattern(pattern.offset - 2)

    for run in pattern.runs:
        while run > 0:
            buffer = (buffer << 1 | bit) & 0b11111  # Slide buffer forward by one bit.
            steps = 1

            # Trivial optimization: if buffer = 00000, no need to read a run of
            # 0s one by one, because the result is always a blank square; and
            # similarly for buffer = 11111 and a run of 1s. In these cases can
            # skip over the entire run.
            if bit + buffer == 0 or bit + buffer == 32:
                steps = run
            p.insert(states[buffer], steps)

            if not p.runs and not p.count:  # Increment offset unless first
                p.offset += steps           # filled square has been written.
            run -= steps

        bit = (bit + 1) % 2

    while buffer > 0:                     # After reading through the pattern,
        buffer = (buffer << 1) & 0b11110  # keep still writing until the buffer
        p.insert(states[buffer])          # is empty.

    return p.complete()



def toPattern(input):
    p = Pattern()

    for c in input:
        if c != '#' and c != '.':
            raise ValueError()
        p.insert(c == '#')

    return p.complete()



def solve(pattern, states):
    t = (0,) + tuple(pattern.runs)  # Cast lists to tuples so that can work with sets...
    lines = set(t)
    patterns = set(t)

    for i in range(100):
        pattern = read(pattern, states)

        if not pattern.runs[0]:  # Got a pattern with no filled squares.
            return 'vanishing'
        t = (pattern.offset,) + tuple(pattern.runs)

        if t in lines:         # Exact same line (offset + pattern) has been
            return 'blinking'  # encountered before.

        lines.add(t)
        t = (0,) + tuple(pattern.runs)

        if t in patterns:     # Exact same pattern has been encountered before,
            return 'gliding'  # but at a different offset.
        patterns.add(t)

    return 'other'



def run():
    try:
        f = open('patterns.txt', 'r')
        start = clock()
        states = calculateStates()

        for line in f.read().splitlines():
            print(solve(toPattern(line), states))

        print('Runtime (s) =', clock() - start)  # I consistently get 0.024~0.032
        f.close()                                # seconds on Intel Core i5-7200U.

    except FileNotFoundError:
        print('Where\'s your patterns.txt, sahib?')
    except:
        print('Oops. Something went sideways.')



run()
