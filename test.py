
from typing import Union
import logging
import time
import sys
# from robot_support.docker import Log
from robot_support.logger import Logger
Logger.get_instance("./logs/new_log.txt", logging.DEBUG)


from robot_support.docker import Container as Engine

# logger = Logger("./logs/new_log.txt")

docker = Engine("robot-postgres")

def start_blank_postgres(tag: str = "12", **kwargs):
    # print(docker)
    return docker.run(f"postgres:{tag}",
        detach=True,
        remove=True,
        log=True,
        environment={
            'POSTGRES_USER': 'user',
            'POSTGRES_DB': 'db',
            'POSTGRES_PASSWORD': 'password'
        },
    )


def stop_blank_postgres():
    docker.stop(5)


if __name__ == "__main__":
    # try:
    #     raise Exception("testing")
    # except Exception as err:
    #     Logger.get_instance().error(err)

    # sys.exit()
    # l = Logger()
    # Logger.LOG_PATH = "./logs/new_log.txt"
    # print(Logger.log_path)
    # print("here")
    # Logger.get_instance()
    # print(Logger.get_instance())

    # print(l)
    # ls = Logger.get_instance()
    # print(ls)
    # l.info("jhhj")
    # ls.info("jhhj")
    process = start_blank_postgres(12)
    time.sleep(2)
    stop_blank_postgres()
