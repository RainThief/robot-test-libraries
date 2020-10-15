"""docker logs module"""


import threading
import docker
from robot_support.logger import Logger


LOGGER = Logger.get_instance()


class Log:
    """Docker logging class

    Extract logs from running docker containers

    Attributes:
        _log_thread: running container process
        _stop_event: coroutine task handling stopping container
        _process: running container process

    Args:
        process: running container process
    """


    def __init__(self, process: docker.models.containers.Container):
        self._log_thread = threading.Thread(target=self._capture)
        self._stop_event = threading.Event()
        self._log_thread.daemon = True
        self._process = process


    def start(self) -> None:
        """start logging capture"""
        self._log_thread.start()


    def stop(self) -> None:
        """stop logging capture"""
        self._stop_event.set()


    def _capture(self) -> None:
        """Captures the docker service logs and writes to a file

        Args:
            service (Service): The service to capture logs
        """
        generator = self._process.logs(follow=True, stdout=True, stderr=True, stream=True)
        while not self._stop_event.is_set():
            try:
                output = next(generator).decode('utf-8').rstrip('\r\n')
                if output == "":
                    continue
                LOGGER.debug(
                    f"DOCKER: {self._process.name}: {output}"
                    .format(self._process.name, output),
                    False
                )
            except StopIteration as err:
                LOGGER.warn("Error getting docker container {} log output: {}".format(self._process.name, err))

        LOGGER.debug("Exited logging thread for {}".format(self._process.name), False)
