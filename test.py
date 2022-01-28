from scipy import sparse
from termcolor import colored
import hashlib
from functools import cached_property


PLAYER_1 = 1.0
PLAYER_2 = 2.0


FOR_WIN = 3

DIRECTIONS = [
    ((1, 0), (-1, 0)),
    ((1, 1), (-1, -1)),
    ((0, 1), (0, -1)),
    ((1, -1), (-1, -1))
]



class Move:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player

    def __str__(self):
        return f'{nice(self.player)} ({self.y}|{self.x})'


def nice(value):
    match value:
        case 1.0:
            return colored('✕', 'green')
        case 2.0:
            return colored('○', 'red')
        case _:        
            return colored('·', 'white')


def hash_matrix(matrix):
    string = ''
    for y in range(matrix.get_shape()[0]):
        for x in range(matrix.get_shape()[1]):
            string += str(int(matrix[y, x]))
    return hashlib.sha1(string.encode()).hexdigest()
    

class Board:
    GENERATED = {}

    def __init__(self, matrix, move):
        self.matrix = matrix
        self.move = move
        self.children = []

        self._tree_generated = False

        Board.GENERATED[self.hash] = self

    def play(self, move):
        matrix = self.matrix.copy()
        matrix[move.y, move.x] = move.player

        matrix_hash = hash_matrix(matrix)
        if matrix_hash in Board.GENERATED:
            child = Board.GENERATED[matrix_hash]
        else:
            child = Board(matrix, move)

        self.children.append(child)
        return child

    @classmethod
    def root_board(cls, height, width):
        matrix = sparse.lil_matrix((height, width))
        return cls(matrix, None)

    @cached_property
    def width(self):
        return self.matrix.get_shape()[1]

    @cached_property
    def height(self):
        return self.matrix.get_shape()[0]

    @property
    def next_player(self):
        if not self.move or self.move.player == PLAYER_2:
            return PLAYER_1
        return PLAYER_2

    @property
    def potential_moves(self):
        next_player = self.next_player
        for y in range(self.height):
            for x in range(self.width):
                if self.matrix[y, x] == 0.0:
                    yield Move(x, y, next_player)

    def __str__(self):
        repr = f'{self.move} {self.hash}\n'
        for y in range(self.height):
            for x in range(self.width):
                repr += ' ' +  nice(self.matrix[y, x])
            repr += '\n'
        return repr

    @cached_property
    def is_draw(self):
        return len(self.matrix.nonzero()[0]) == (self.width * self.height)

    def generate_tree(self):
        if not self._tree_generated:
            print(self)
            if not self.is_draw and not self.is_win:
                self._tree_generated = True
                for move in self.potential_moves:
                    sub_board = self.play(move)
                    sub_board.generate_tree()
    
    @cached_property
    def hash(self):
        return hash_matrix(self.matrix)

    def vector_len(self, vector, x, y):
        try:
            if self.matrix[y, x] == self.move.player:
                x += vector[0]
                y += vector[1]
                return 1 + self.vector_len(vector, x, y)
            return 0
        except IndexError:
            return 0

    @cached_property
    def is_win(self):
        if self.move:
            x, y = self.move.x, self.move.y
            for vectors in DIRECTIONS:
                v1_len = self.vector_len(vectors[0], x, y)
                v2_len = self.vector_len(vectors[1], x, y)
                if (v1_len + v2_len - 1) >= FOR_WIN:
                    return True
        return False



b1 = Board.root_board(10, 10)
b1.generate_tree()
# print(len(Board.GENERATED))

