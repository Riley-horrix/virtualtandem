import unittest

from src.task_handler import *

class TestTaskHandler(unittest.TestCase):
    def test_repeating_tasks_run_and_cancel(self):
        task_handler = TaskHandler()
        repeat_num = []

        task_repeat = Task(lambda _: repeat_num.append(0))
        repeat_handle = task_handler.task_interval(task_repeat, 1)


        task_cancel = Task(lambda _: repeat_handle.cancel())
        task_handler.task_delay(task_cancel, 100)

        task_handler.start()
        self.assertAlmostEqual(len(repeat_num), 80, delta=10.0)

    def test_tasks_run(self):
        task_handler = TaskHandler()
        task_list = []

        task1 = Task(lambda _: task_list.append(1))
        task2 = Task(lambda _: task_list.append(2))
        task3 = Task(lambda _: task_list.append(3))

        # Should print task3, task1, task2
        task_handler.task_delay(task1, 10)
        task_handler.task_delay(task2, 20)
        task_handler.task_delay(task3, 5)

        task_handler.start()
        self.assertListEqual(task_list, [3, 1, 2])

    def test_task_can_create_task(self):
        task_handler = TaskHandler()
        task_list = []

        def create_tasks(_: TaskHandle):
            child_task1 = Task(lambda _: task_list.append(1))
            child_task2 = Task(lambda _: task_list.append(2))
            task_handler.task_delay(child_task1, 20)
            task_handler.task_delay(child_task2, 10)
            task_list.append(0)

        parent = Task(create_tasks)
        task_handler.task_delay(parent, 0)
        task_handler.start()

        self.assertListEqual(task_list, [0, 2, 1])

    def test_task_can_cancel_itself(self):
        task_handler = TaskHandler()
        task_list = [0]

        def cancelling_task(handle: TaskHandle):
            if task_list[0] == 5:
                handle.cancel()
                return
            task_list[0] += 1

        task = Task(cancelling_task)
        task_handler.task_interval(task, 5)
        task_handler.start()
        self.assertListEqual(task_list, [5])

if __name__ == "__main__":
    unittest.main()