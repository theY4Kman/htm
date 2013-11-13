class Cell(object):
    INACTIVE = 0
    ACTIVE = 1
    PREDICTIVE = 2

    state = INACTIVE


class DendriteSegment(object):
    def __init__(self, owner):
        self.owner = owner


class Synapse(object):
    """A relationship between a dendrite segment and a Cell"""
    pass


class Column(object):
    """An ordered list of cells representing a column"""
    def __init__(self, cells_per_col, cell_cls=Cell):
        self.cells_per_col = cells_per_col
        self.cell_cls = cell_cls

        self.cells = self._build_cells(self.cells_per_col, self.cell_cls)

    @staticmethod
    def _build_cells(cells_per_col, cell_cls):
        return [cell_cls() for _ in xrange(cells_per_col)]


class Layer(object):
    """A 2D grid of Columns"""

    def __init__(self, length=10, width=100, cells_per_col=4, col_class=Column):
        self.length = length
        self.width = width
        self.cells_per_col = cells_per_col
        self.col_class = col_class

        self.columns = self._build_columns(self.length, self.width,
                                           self.cells_per_col, self.col_class)

    @staticmethod
    def _build_columns(length, width, cells_per_col, col_class):
        columns = []
        for _ in xrange(length):
            row = []
            for _ in xrange(width):
                row.append(col_class(cells_per_col))
            columns.append(row)
        return columns


class HTM(object):
    def __init__(self, format=(1, 4)):
        """
        @type   format: tuple
        @param  format: Denotes the number of cells per column for each layer
            in the HTM. The first entry represents the bottom-most layer (where
            input comes from the bottom)
        """
        self.format = format
        self.layers = self._create_layers(self.format)

    @staticmethod
    def _create_layers(format):
        return [Layer(cells_per_col) for cells_per_col in xrange(format)]
