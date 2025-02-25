from src.lib.time_utils import current_time_ms, sleep_ms


class TaskHandle:
    """
    Task handler class.
    """
    def __init__(self, uid: int, task_handler: "TaskHandler"):
        self.uid: int = uid
        self.task_handler = task_handler

    def cancel(self):
        self.task_handler.remove_task(self)


def task_function(_: TaskHandle) -> None:
    return None

type task_func_t = type(task_function)


class Task:
    def __init__(self, func: task_func_t):
        self.task = func


class _TaskQueueTask:
    def __init__(self, task: Task, delay_ms: int, handle: TaskHandle, repeating: bool = False):
        self.handle = handle
        self.cancelled = False
        self.func = task.task
        self.time = abs(delay_ms) + current_time_ms() if not repeating else current_time_ms()
        self.delay = abs(delay_ms)
        self.repeating = repeating
        self.executing = False

class TaskHandler:
    """
    Main task handler / event loop.

    You can use this class to queue tasks and intervals, and also cancel them.
    """
    def __init__(self):
        self.uid_gen = 0
        self.task_queue: list[_TaskQueueTask] = []

    def task_delay(self, task: Task, delay_ms: int) -> TaskHandle:
        """
        Queue a delayed task.

        :param task: The task to delay.
        :param delay_ms: The delay in ms until the task should be executed.

        :return: A unique handle for the task. Can be used to cancel a task.
        """
        self.uid_gen += 1
        handle = TaskHandle(self.uid_gen, self)
        self.__insert_task(_TaskQueueTask(task, delay_ms, handle))
        return handle

    def task_interval(self, task: Task, delay_ms: int) -> TaskHandle:
        """
        Queue a repeating task.

        :param task: The task to queue.
        :param delay_ms: The interval in ms of the queued task.
        :return: A unique handle for the task. Can be used to cancel a task.
        """
        self.uid_gen += 1
        handle = TaskHandle(self.uid_gen, self)
        self.__insert_task(_TaskQueueTask(task, delay_ms, handle, repeating=True))
        return handle

    def __insert_task(self, task_to_add: _TaskQueueTask) -> None:
        """
        Insert a task into the task queue.

        This function ensures that the task queue list is ordered by time.

        :param task_to_add: The task to add.
        :return: None
        """
        i = 0
        # Find correct index
        for task in self.task_queue:
            if task_to_add.time >= task.time: # Needs to be >= to catch skipping this task
                i += 1
                continue
            break
        self.task_queue.insert(i, task_to_add)

    def start(self) -> None:
        """
        Starts the task handler.

        This should be the main running loop of the program, and loops over the tasks in the task queue.

        Once the task queue is empty, this function returns. This means that  a user needs to queue tasks before calling this function.

        :return: None
        """
        while self.task_queue:
            # Get the next task to execute
            task = self.task_queue[0]

            # Just pop if task is cancelled
            if task.cancelled:
                self.task_queue.pop(0)
                continue

            # If in the future then delay
            time = current_time_ms()
            if task.time > time:
                sleep_ms(task.time - time)

            # Execute task
            task.executing = True
            task.func(task.handle)

            # Requeue if repeating and not cancelled
            if task.repeating and not task.cancelled:
                task.time = task.delay + current_time_ms()
                self.__insert_task(task)

            self.task_queue.pop(0)

    def __find_task(self, uid: int) -> tuple[int, _TaskQueueTask] | None:
        """
        Find a task in the task queue by its unique identifier.

        :param uid: The task's unique identifier.
        :return: If the task is in the task queue, it returns a tuple containing (index, task), else it returns None.
        """
        for i, task in enumerate(self.task_queue):
            if task.handle.uid == uid:
                return i, task
        return None


    def remove_task(self, handle: TaskHandle) -> bool:
        """
        Remove a task from the task queue.

        :param handle: The handle returned from creating a task.
        :return: True if the task existed, False otherwise.
        """
        found_task = self.__find_task(handle.uid)
        if found_task:
            (i, task) = found_task
            # If task currently running, just set cancelled flag
            if task.executing:
                task.cancelled = True
            # Else pop task from the queue
            else:
                self.task_queue.pop(i)
            return True
        return False
