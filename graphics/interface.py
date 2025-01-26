import numpy as np

if __name__ == '__main__':
    import graphics as gp
else:
    import graphics.graphics as gp

class TandemGraphics():
    def __init__(self):
        self.window = gp.GraphWin("VirtualTandem", 400, 400)
        self.window.setCoords(-1,-1,1,1)
        self.robot_radius = 0.1
        self.__setup_robot__()
        self.robot_body.draw(self.window)
        self.robot_dir.draw(self.window)
        self.trail = []
        self.prev_x = 0
        self.prev_y = 0

    def updateRobot(self, x, y, orientation):
        self.robot_body.move(x - self.prev_x, y - self.prev_y)

        self.robot_dir.undraw()
        self.robot_dir = self.__get_origin_direction(orientation)
        self.robot_dir.move(x, y)
        self.robot_dir.draw(self.window)

        trail_line = gp.Line(gp.Point(self.prev_x, self.prev_y), gp.Point(x, y))
        self.prev_x = x
        self.prev_y = y
        trail_line.draw(self.window)
        self.trail.append(trail_line)
        self.window.redraw()
        self.window.getMouse()

    def __get_origin_direction(self, orientation):
        tip = gp.Point(np.sin(np.deg2rad(orientation)) * self.robot_radius * 2, np.cos(np.deg2rad(orientation)) * self.robot_radius * 2)
        left = gp.Point(np.sin(np.deg2rad(orientation - 15)) * self.robot_radius, np.cos(np.deg2rad(orientation - 15)) * self.robot_radius)
        right = gp.Point(np.sin(np.deg2rad(orientation + 15)) * self.robot_radius, np.cos(np.deg2rad(orientation + 15)) * self.robot_radius)
        return gp.Polygon(tip, left, right)

    def __setup_robot__(self):
        self.robot_body = gp.Circle(gp.Point(0, 0), self.robot_radius)
        self.robot_dir = self.__get_origin_direction(0)

if __name__ == '__main__':
    graphics = TandemGraphics()
    points = []
    orientations = []
    for i in range(1, 10):
        points.append((i / 10.0, i / 10.0))
        orientations.append(i * 36.0)

    for i in range(1, 9):
        graphics.updateRobot(points[i][0], points[i][1], orientations[i])