"""docker container module"""


import asyncio
import sys
import time
from typing import Dict, Any, Optional
import docker
from robot_support.logger import Logger
from robot_support.docker_lib.log import Log


LOGGER = Logger.get_instance()


try:
    client: docker.client.DockerClient = docker.from_env()
except docker.errors.DockerException as error:
    LOGGER.error(error)
    LOGGER.error("cannot connect to docker socket")
    sys.exit(1)


class Container:
    """Docker container wrapper class

    Controlls starting and stopping of docker containers

    Attributes:
        name: container name
        stop_task: coroutine task handling stopping container
        process: docker container process
        logs: Docker log capture object

    Args:
        name: container name
    """


    def __init__(self, name: str):
        self.name: str = name
        self.stop_task: asyncio.Task = None
        self.process: docker.models.containers.Container = None
        self.logs: Log = None


    def run(self, image: str, **kwargs: Dict[str, Any]) -> None:
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

        log = None
        if 'log' in kwargs:
            log = kwargs.pop('log')

        kwargs['name'] = self.name

        LOGGER.info(f"starting docker container {self.name} from image {image}")

        self.process = client.containers.run(
            image,
            command,
            **kwargs
        )

        self.logs = Log(self.process)

        if log:
            self.logs.start()


    def stop(self, grace_time: Optional[int] = 10) -> None:
        """Stop docker container task

        Args:
            grace_time: timout before sigkill
        """
        async def stop_container():
            kill_task = asyncio.ensure_future(self._kill(grace_time))
            self.stop_task = asyncio.ensure_future(self._stop(kill_task, grace_time))

            self.logs.stop()

            try:
                await asyncio.gather(kill_task, self.stop_task)
            except asyncio.exceptions.CancelledError:
                # if kill task is cancelled due to successful stop task
                pass

        asyncio.run(stop_container())


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
        LOGGER.info(f"stopping docker container {self.name}")
        # for better logging we are handling our own sigkill
        # so add 1 to timout so will not be called
        self.process.stop(timeout=grace_time+1)
        LOGGER.debug(f"container {self.name} stopped in {int(time.time() - time_start)} seconds", False)
        kill_task.cancel()


    async def _kill(self, grace_time: int) -> None:
        """Kill docker container task

        Args:
            grace_time: timout before sigkill
        """
        await asyncio.sleep(grace_time)
        self.stop_task.cancel()
        self.process.kill()
        LOGGER.warn(f"killing docker container {self.name} after failed stop within {grace_time} seconds")
