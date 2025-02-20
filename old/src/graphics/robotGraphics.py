import math

if __name__ == '__main__':
    import graphics as gp
else:
    import graphics.graphics as gp

class RobotGraphics:
    def __init__(self, window, base_width, wheel_radius, wheel_width, x=0, y=0, o=0):
        self.path: list[tuple[int, int]] = []
        self.x = x
        self.y = y
        self.o = o

        self.window = window

        self.polygon = None

        self.col = "#fff"

        self.width = base_width
        self.height = base_width * 0.7

        self.wheelWidth = wheel_width
        self.wheelHeight = wheel_radius * 2

    def updateRobot(self, dx=0, dy=0, do=0):
        self.path.append((self.x, self.y))
        self.x += dx
        self.y += dy
        self.o += do

        if do == 0 and self.polygon:
            self.polygon.move(dx, dy)
            return

        # Points on the robot to draw it
        # Duplicate wheel edges closest to the robot to ensure a line is drawn
        robotPoints = [
            # Rectangle
            (-self.width / 2, self.height / 2),
            # Left wheel 
            (-self.width / 2, -self.wheelHeight / 2),
            (-self.width / 2, self.wheelHeight / 2),
            (-self.width / 2 - self.wheelWidth, self.wheelHeight / 2),
            (-self.width / 2 - self.wheelWidth, -self.wheelHeight / 2),
            (-self.width / 2, -self.wheelHeight / 2),
            # Rectangle
            (-self.width / 2, -self.height / 2),
            (self.width / 2, -self.height / 2),
            # Right wheel
            (self.width / 2, self.wheelHeight / 2),
            (self.width / 2, -self.wheelHeight / 2),
            (self.width / 2 + self.wheelWidth, -self.wheelHeight / 2),
            (self.width / 2 + self.wheelWidth, self.wheelHeight / 2),
            (self.width / 2, self.wheelHeight / 2),
            # Rectangle
            (self.width / 2, self.height / 2),
            # Direction triangle on front
            (self.width / 4, self.height / 2),
            (0, self.height / 1.3),
            (-self.width / 4, self.height / 2)
        ]

        cosO = math.cos(math.radians(self.o))
        sinO = math.sin(math.radians(self.o))

        transformedPoints = [
            gp.Point(cosO * pointX - sinO * pointY + self.x, sinO * pointX + cosO * pointY + self.y) for (pointX, pointY) in robotPoints
        ]

        current = self.polygon

        self.polygon = gp.Polygon(transformedPoints)
        self.polygon.setFill(self.col)

        self.polygon.draw(self.window)

        if current:
            current.undraw()

if __name__ == '__main__':
    import time
    window = gp.GraphWin("VirtualTandem", 400, 400)
    window.setCoords(-3, -3, 3, 3)
    rob = RobotGraphics(window)

    while True:
        rob.updateRobot(dx = 0.01, dy=0.01, do=1)
