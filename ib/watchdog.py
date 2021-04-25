# watchdog.py
# worker thread to periodically perform a desired watchdog_task

import time
from threading import Thread


class Watchdog(Thread):
    watchdog_timeout_sec: int

    # constructor
    def __init__(self, timeout_sec=10, autostart=False):
        # start a background thread that periodically performs a watchdog_task
        Thread.__init__(self)
        self.daemon = True
        self.watchdog_timeout_sec = timeout_sec

        # False => user wants to manually kick off the watchdog sometime in the future
        if autostart:
            self.start()

    # Thread execution watchdog_task.
    # Call "kill_watchdog" or manually set timeout to 0 to terminate
    def run(self):
        while True:
            if self.watchdog_timeout_sec >= 1:
                self.watchdog_task()
                time.sleep(self.watchdog_timeout_sec)
            else:
                print("==== WATCHDOG INACTIVE ====")
                break

    # manually set the timeout to 0 to kill the watchdog process on its next pass.
    # TODO: Kill process immediately
    def kill_watchdog(self):
        self.watchdog_timeout_sec = 0

    # watchdog watchdog_task. Sub-class and override to do something useful
    def watchdog_task(self):
        print(f'WATCHDOG TIMEOUT={self.watchdog_timeout_sec}')


if __name__ == '__main__':
    print("=== Watchdog.py ===")
