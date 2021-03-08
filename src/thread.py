import threading


class Thread:
    __interrupt = False
    __event = None

    @staticmethod
    def name():
        return threading.current_thread().getName()

    @staticmethod
    def set_interrupt(interrupt):
        Thread.__interrupt = interrupt

    @staticmethod
    def get_interrupt():
        return Thread.__interrupt


def thread(name=None, daemon=False):
    """
    Creates a thread for a given function
    """
    def wrapper(function):
        def decorator_thread(*args):
            thread = threading.Thread(target=function, args=args, daemon=daemon)
            thread.setName(name) if name != None else\
                thread.setName(function.__name__ + "_thread")
            thread.start()
            return thread
        return decorator_thread
    return wrapper
