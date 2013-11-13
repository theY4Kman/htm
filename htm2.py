# So, this is my attempt at just getting shit done, fuck the design. Gonna
# implement the HTM pseudocode pretty much 1:1


# Arbitrary value for now
from random import randint, random

CONNECTED_PERM = 0.7
# Range +/- CONNECTED_PERM used to initialize potential synapse permanences
CONNECTED_PERM_INITIAL_RANGE = 0.15

# The number of synapses to initialize each column with
NUM_INIT_POTENTIAL_SYNAPSES = 10
# The range around which synapses should form around a column's center
RANGE_INIT_POTENTIAL_SYNAPSES = 4

MIN_OVERLAP = None


class Synapse(object):
    def __init__(self, column, x, y, permanence):
        self.column = column
        self.x = x
        self.y = y
        self.permanence = permanence

    def input(self, t):
        return self.column.grid.input(t, self.x, self.y)


class Column(object):
    def __init__(self, grid, x, y):
        self.grid = grid
        self.x = x
        self.y = y

        self.overlap = 0.0

        self._initialize_synapses()

    @property
    def connected_synapses(self):
        for syn in self.synapses:
            if syn.permanence >= CONNECTED_PERM:
                yield syn

    def _initialize_synapses(self):
        self.synapses = []
        c_x, c_y = randint(0, self.grid.width), randint(0, self.grid.length)
        for _ in xrange(NUM_INIT_POTENTIAL_SYNAPSES):
            r_x = randint(-RANGE_INIT_POTENTIAL_SYNAPSES, RANGE_INIT_POTENTIAL_SYNAPSES)
            r_y = randint(-RANGE_INIT_POTENTIAL_SYNAPSES, RANGE_INIT_POTENTIAL_SYNAPSES)

            x = max(min(c_x + r_x, self.grid.width-1), self.grid.length-1)
            y = max(min(c_y + r_y, self.grid.width-1), self.grid.length-1)

            # TODO: still have a random range around the center, somehow including
            #       distance from the center in the random range around what is
            #       calculated below
            permanence = CONNECTED_PERM + (random() - 0.5) * CONNECTED_PERM_INITIAL_RANGE
            syn = Synapse(self, x, y, permanence)
            self.synapses.append(syn)


class ColumnGrid(object):
    def __init__(self, length, width, input_stream):
        self.length = length
        self.width = width

        self.columns = [[Column(self, x, y) for y in xrange(self.length)]
                        for x in xrange(self.width)]

        # Should be an object with a read() method which returns a grid of
        # booleans in the same format as self.columns
        self.input_stream = input_stream
        self.past_input = []

    def iter_columns(self):
        for x in xrange(self.width):
            for y in xrange(self.length):
                yield self.columns[x][y]

    def input(self, t, x, y):
        self._read_input_till(t)
        return self.past_input[t][x][y]

    def _read_input_till(self, t):
        while len(self.past_input) <= t:
            self.past_input.append(self.input_stream.read())


class SampleInput(object):
    """Basic input which yields a growing square

    0000000000 0000000000 0000000000 0000000000 0000000000 1111111111
    0000000000 0000000000 0000000000 0000000000 0111111110 1000000001
    0000000000 0000000000 0000000000 0011111100 0100000010 1000000001
    0000000000 0000000000 0001111000 0010000100 0100000010 1000000001
    0000000000 0000110000 0001001000 0010000100 0100000010 1000000001
    0000000000 0000110000 0001001000 0010000100 0100000010 1000000001
    0000000000 0000000000 0001111000 0010000100 0100000010 1000000001
    0000000000 0000000000 0000000000 0011111100 0100000010 1000000001
    0000000000 0000000000 0000000000 0000000000 0111111110 1000000001
    0000000000 0000000000 0000000000 0000000000 0000000000 1111111111
    """

    def __init__(self):
        self.radius = 0
        self.width = 10
        self.length = 10

    def read(self):
        out = [[False] * self.length for _ in xrange(self.width)]
        c_x = self.width / 2
        c_y = self.length / 2

        for x in xrange(c_x - self.radius, c_x + self.radius + 1):
            out[x][c_y - self.radius] = True
            out[x][c_y + self.radius] = True

        for y in xrange(c_y - self.radius, c_y + self.radius + 1):
            out[c_x - self.radius][y] = True
            out[c_x + self.radius][y] = True

        self.radius += 1
        if self.radius >= c_x:
            self.radius = 0

        return out


columns = ColumnGrid(10, 10, SampleInput())
curtime = 0


def spatial_phase_1():
    for col in columns.iter_columns():
        col.overlap = 0.0
        for syn in col.connected_synapses:
            col.overlap += syn.input(curtime)
