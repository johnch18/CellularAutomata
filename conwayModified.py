#!/usr/bin/python3

import math
import random
import time
from typing import Optional, List, Tuple, Union, Dict
import pygame


def clamp(x: float, lo: float, hi: float):
    if x < lo:
        return lo
    elif x > hi:
        return hi
    return x


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, point: Union[Tuple[int, int], "Point"]):
        return Point(self[0] + point[0], self[1] + point[1])

    def __mul__(self, scale: int):
        return self.get_scaled(scale)

    def __hash__(self):
        return hash((self.length, self.angle))

    def __getitem__(self, item: int):
        return [self.x, self.y][item]

    def __eq__(self, other: Union[Tuple[int, int], "Point"]):
        return self[0] == other[0] and self[1] == other[1]

    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    def get_scaled(self, scale: int):
        return Point(self[0] * scale, self[1] * scale)


PRINCIPLE_POINTS = [
    Point(1, 0), Point(1, 1),
    Point(0, 1), Point(-1, 1),
    Point(-1, 0), Point(-1, -1),
    Point(0, -1), Point(1, -1)
]


class Cell:
    MAX_STATE = 5

    def __init__(self, loc: Point, state: int = 0, dirty: bool = False):
        self.loc = loc
        self.state = state
        self.__tempState = 0
        self.dirty = True

    def __str__(self):
        return f"{self.state}"

    def __repr__(self):
        return f"Cell<{self.state}>"

    def cycle(self, longerLife=False):
        amount = 1 if longerLife else -1
        self.adjust_cell(amount)

    def adjust_cell(self, amount: int):
        self.__tempState = clamp(self.state + amount, 0, Cell.MAX_STATE)
        self.dirty = True

    def update(self):
        self.state = self.__tempState
        self.dirty = False

    def get_neighbors(self, board: "Board"):
        for principle in PRINCIPLE_POINTS:
            new_point = self.loc + principle
            if new_point in board.cells and not board.cells[new_point].dirty:
                yield board.cells[new_point]
            elif new_point not in board.cells:
                board.cells[new_point] = Cell(new_point, 0, dirty=True)
                yield board.cells[new_point]

    def is_alive(self):
        return self.state > 0

    def can_grow(self, food):
        if self.state >= 5:
            return False
        if 4 < food < 30 or food < 2:
            return True
        return False


class Board:

    def __init__(self, newCells: List[Cell]):
        self.cells: Dict[Point, Cell] = dict()
        self.load_cells(newCells)

    def do_cycle(self):
        cellsToUpdate = set()
        for cell in self.cells.copy().values():
            for cell2 in cell.get_neighbors(self):
                cellsToUpdate.add(cell2)
        for cell in cellsToUpdate:
            neighbors = cell.get_neighbors(self)
            food = sum(map(lambda c: c.state, neighbors))
            grow = cell.can_grow(food)
            cell.cycle(grow)

    def update(self):
        for cell in self.cells.values():
            cell.update()

    def load_cells(self, newCells: List[Cell]):
        for cell in newCells:
            self.cells[cell.loc] = cell

    def do_tick(self):
        alive = self.num_alive()
        print(f"{alive} cells alive")
        self.do_cycle()
        self.update()
        return alive

    def run(self, maxRuns=-1):
        alive = 1
        while alive > 0:
            alive = self.do_tick()

    def num_alive(self) -> int:
        alive = 0
        for cell in self.cells.values():
            if cell.is_alive():
                alive += 1
        return alive


class PyBoard(Board):
    def __init__(self, newCells, window, clock):
        super().__init__(newCells)
        self.window = window
        self.clock = clock

    def do_tick(self):
        super().do_tick()
        self.draw()

    def run_pygame(self):
        running = True
        frame = 0
        while running:
            frame += 1
            self.window.fill((255, 255, 255))
            self.do_tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.image.save(self.window, "screenshots/conway-screenshot-{:04d}.png".format(frame))
            pygame.display.flip()
            self.clock.tick(1)

    def draw(self):
        for position, cell in self.cells.items():
            color = (math.floor(255 * (cell.state / 5)), 0, 0)
            offset = 400
            newPosition = position.get_scaled(5)
            pos = (newPosition.x + offset, newPosition.y + offset)
            size = (5, 5)
            pygame.draw.rect(self.window, color, pygame.Rect(*pos, *size))


def pygame_stuff():
    pygame.init()
    window = pygame.display.set_mode((800, 800))
    return window


def render():
    window = pygame_stuff()
    clock = pygame.time.Clock()
    cells = [Cell(Point(x, y), random.randint(0, 2)) for x in range(-10, 10) for y in range(-10, 10)]
    test = PyBoard(cells, window, clock)
    test.run_pygame()


render()
