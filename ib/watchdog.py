# watchdog.py


import time
from threading import Thread
from loguru import logger


class Watchdog(Thread):
    # TODO: Document Watchdog class
    """
    Watchdog
    Background task which periodically performs one or more functions.
    Parameters:
        - timeout_sec (10)= Interval for watchdog timer in seconds.
        - autostart (False) = Start background task immediately. Use start() for manual initiation.
    """
    def __init__(self, timeout_sec=10, autostart=False):
        Thread.__init__(self)
        self.daemon = True
        self.watchdog_timeout_sec = timeout_sec

        # False => user will manually call start() sometime in the future
        if autostart:
            self.start()

    def run(self):
        while True:
            if self.watchdog_timeout_sec >= 1:
                self.watchdog_task()
                time.sleep(self.watchdog_timeout_sec)
            else:
                logger.log('INFO', 'Watchdog disabled')
                break

    def kill_watchdog(self):
        """ Permanently halts operation of the watchdog task """
        self.watchdog_timeout_sec = 0

    def watchdog_task(self):
        """ Called once each watchdog period """
        logger.log('INFO', f'WATCHDOG TIMEOUT={self.watchdog_timeout_sec}')


if __name__ == '__main__':
    print("=== Watchdog.py ===")
