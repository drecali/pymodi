import setproctitle

import multiprocessing as mp

from modi._serial_task import SerialTask


class SerialProcess(mp.Process):
    """
    :param queue serial_read_q: Multiprocessing Queue for serial reading data
    :param queue serial_write_q: Multiprocessing Queue for serial writing data
    """

    def __init__(self, serial_read_q, serial_write_q):
        super(SerialProcess, self).__init__()
        self.__ser_task = SerialTask(serial_read_q, serial_write_q)
        self.__stop = mp.Event()

        setproctitle.setproctitle('pymodi-serial')

    def run(self):
        """ Run serial task
        """

        while not self.stopped():
            self.__ser_task.run()
        self.__ser_task.close_serial()

    def stop(self):
        """ Stop serial task
        """

        self.__stop.set()

    def stopped(self):
        """ Check serial task status
        """

        return self.__stop.is_set()
