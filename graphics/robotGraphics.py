import graphics as gp
from graphics.graphics import GraphicsObject

class Robot:
    def __init__(self, x=0, y=0, o=0):
        self.path: list[tuple[int, int]] = []
        self.x = x
        self.y = y
        self.o = o
        self.drawRobot()

    def drawRobot(self, dx=0, dy=0, do=0):
        self.path.append((self.x, self.y))
        self.x += dx
        self.y += dy
        self.o += do

        gp = self.context

        objects = [
            gp.Rectangle(gp.Point(), gp.Point())
        ]



