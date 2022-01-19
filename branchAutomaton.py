#!/usr/bin/python3
import pygame.draw


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other: "Point"):
        return self.x == other.x and self.y == other.y

    def __neq(self, other: "Point"):
        return not self.__eq__(other)

    def __add__(self, other: "Point"):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, scaleFactor):
        return Point(self.x * scaleFactor, self.y * scaleFactor)

    def to_list(self):
        return [self.x, self.y]

    def scale(self, sFactor: int):
        return self * sFactor


class Line:
    def __init__(self, source: Point, theta: int = 0):
        self.source = source
        self.theta = theta % 8
        self.done = False
        # Theta = 0...7 <=> 0...2pi

    @property
    def dest(self):
        tTable = [
            Point(1, 0),
            Point(1, 1),
            Point(0, 1),
            Point(-1, 1),
            Point(-1, 0),
            Point(-1, -1),
            Point(0, -1),
            Point(1, -1)
        ]
        return self.source + tTable[self.theta]

    def get_left_child(self):
        return Line(self.dest, self.theta + 1)

    def get_right_child(self):
        return Line(self.dest, self.theta - 1)

    def draw(self, surface, offset=Point(0, 0), sFactor=1):
        pygame.draw.line(surface, (0, 0, 0), (self.source.scale(sFactor) + offset).to_list(),
                         (self.dest.scale(sFactor) + offset).to_list(),
                         2)


class Board:
    def __init__(self, lines):
        self.lines = lines
        self.pointsList = []

    def draw(self, surface, offset, scale):
        for line in self.lines:
            line.draw(surface, offset, scale)

    def iterate(self):
        print("Num Lines:", len(self.lines))
        it = 0
        curPoints = self.pointsList[:]
        for line in self.lines[:]:
            if line.done or line.dest in curPoints:
                continue
            it += 1
            self.lines.append(line.get_left_child())
            self.lines.append(line.get_right_child())
            self.pointsList.append(line.dest)
            self.pointsList.append(line.source)
            line.done = True
        print("Num Points:", len(self.pointsList))
        print("Iterations:", it)


def test():
    pygame.init()
    lines = [
        Line(Point(0, 0), 0),
        Line(Point(0, 0), 2),
        Line(Point(0, 0), 4),
        Line(Point(0, 0), 6),
    ]
    board = Board(lines)
    run = True
    surface = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    baseScale = 15
    scaleDrop = 0.99
    curScale = baseScale
    frame = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        surface.fill((255, 255, 255))
        board.iterate()
        board.draw(surface, offset=Point(500, 500), scale=curScale)
        pygame.display.flip()
        clock.tick(60)
        curScale = curScale * scaleDrop
        pygame.image.save(surface, "screenshots/screenshot-{:04d}.png".format(frame))
        frame += 1
        if frame > 50:
            break


def main():
    test()


if __name__ == "__main__":
    main()
