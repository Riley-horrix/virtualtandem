from src.robot import Robot


class Main:
    @staticmethod
    def start():
        robot = Robot()
        robot.start()

if __name__ == '__main__':
    Main.start()