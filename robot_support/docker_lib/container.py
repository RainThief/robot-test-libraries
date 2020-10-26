"""docker container module"""


import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
import docker
from robot_support.logger import Logger
from robot_support.docker_lib.log import Log
from robot_support.errors import ServiceNotReadyError, ServiceFailedError



LOGGER = Logger.get_instance()


try:
    client: docker.client.DockerClient = docker.from_env()
except docker.errors.DockerException as error:
    raise ServiceFailedError("cannot connect to docker socket") from error


class Container:
    """Docker container wrapper class

    Controlls starting and stopping of docker containers

    Attributes:
        _name: container name
        _stop_task: coroutine task handling stopping container
        _process: docker container process
        _logs: Docker log capture object

    Args:
        name: container name
    """


    def __init__(self, name: str):
        self._name: str = name
        self._stop_task: asyncio.Task = None
        self._process: docker.models.containers.Container = None
        self._logs: Log = None


    def run(self, image: str, grace_time: Optional[int] = 10, **kwargs: Dict[str, Any]) -> None:
        """Run container

        Args:
            image: docker image name [image]:[tag]
            **kwargs: arbitrary keyword arguments
                see https://docker-py.readthedocs.io/en/stable/containers.html
                with additional command and log args
        """
        command = None
        if 'command' in kwargs:
            command = kwargs.pop('command')

        readycheck = None
        if 'readycheck' in kwargs:
            readycheck = kwargs.pop('readycheck')

        log = None
        if 'log' in kwargs:
            log = kwargs.pop('log')

        kwargs['name'] = self._name

        LOGGER.info(f"starting docker container {self._name} from image {image}")

        self._process = client.containers.run(
            image,
            command,
            **kwargs
        )

        self._logs = Log(self._process)

        if log:
            self._logs.start()

        if readycheck:
            self._ready_check(grace_time, readycheck[0], *readycheck[1])


    def stop(self, grace_time: Optional[int] = 10) -> None:
        """Stop docker container task

        Args:
            grace_time: timout before sigkill
        """
        async def stop_container():
            kill_task = asyncio.ensure_future(self._kill(grace_time))
            self._stop_task = asyncio.ensure_future(self._stop(kill_task, grace_time))

            self._logs.stop()

            try:
                await asyncio.gather(kill_task, self._stop_task)
            except asyncio.exceptions.CancelledError:
                # if kill task is cancelled due to successful stop task
                pass

        asyncio.run(stop_container())


    def _ready_check(self, grace_time: int, func: Callable[..., None], *args: List[Any]) -> None:
        """Runs a callable function to check container is ready

        Args:
            grace_time: timeout before sigkill
            func: function to run to check readiness
            *args: function arguments
        """
        retries = 0
        ready = False
        LOGGER.info(f"waiting for container {self._name} to be ready")
        while not ready:
            try:
                LOGGER.debug(f"checking {self._name} readiness iteration {retries}", False)
                func(*args)
                ready = True
                LOGGER.info(f"container {self._name} is now ready")
            except ServiceNotReadyError as error:
                if retries == grace_time:
                    raise ServiceFailedError(f"starting container {self._name} failed", error) from error
                retries += 1
                time.sleep(1)
                LOGGER.debug(error, False)


    async def _stop(self, kill_task: asyncio.Task, grace_time: int) -> None:
        """Stop docker container task

        Args:
            kill_task: kill task as asyncio future
            grace_time: timout before sigkill
        """
        time_start = time.time()
        # I have no idea why this happens but without a sleep the event loop
        # gets blocked and the container takes an extra 10 seconds to stop
        await asyncio.sleep(1)
        LOGGER.info(f"stopping docker container {self._name}")
        # for better logging we are handling our own sigkill
        # so add 1 to timout so will not be called
        self._process.stop(timeout=grace_time+1)
        LOGGER.debug(f"container {self._name} stopped in {int(time.time() - time_start)} seconds", False)
        kill_task.cancel()


    async def _kill(self, grace_time: int) -> None:
        """Kill docker container task

        Args:
            grace_time: timout before sigkill
        """
        await asyncio.sleep(grace_time)
        self._stop_task.cancel()
        self._process.kill()
        LOGGER.warn(f"killing docker container {self._name} after failed stop within {grace_time} seconds")
