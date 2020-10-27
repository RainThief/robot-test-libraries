# Robot Support

This project contains libraries for common system testing functionality to be used with [Robot Framework](https://robotframework.org/)

## Requirements

To run system tests using this library you will need

* [Python 3.8+](https://www.python.org/) 
* [Git](https://git-scm.com/)
* [Robot framework](https://robotframework.org/)
* [Docker](https://docs.docker.com/get-docker/)

For developing libraries

* Bash
  * [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
  * [Cygwin](https://www.cygwin.com/)

## Installation

The libraries are installable as a package `robot_support` via pip + git

```shell
pip install git+https://github.com/RainThief/robot-test-libraries.git
```

## Running tests

Run robot framework via cli. For detailed usage please see [user guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#starting-test-execution)

```shell
robot --loglevel INFO ./<test dir>/*.robot
```

## Docker

Instead of installing this package into your project containing your app to be tested, you can mount your project into the robot support container

```shell
docker run --rm -it \
-v <project dir>:/usr/app \
-v /var/run/docker.sock:/var/run/docker.sock \
--network=host \
docker.pkg.github.com/rainthief/robot-test-libraries/robot_testing:latest \
robot --loglevel INFO ./<test dir>/*.robot
```

## Development

In development you can install this library for usage with your new features by installing from your feature branch i.e.

```shell
 pip install git+https://github.com/RainThief/robot-test-libraries.git@<branch name>
```

### Project structure

#### `/.github`

Github actions CI workflows

#### `/robot_support`

Robot support Python package. The code and libraries for this project.

### Commands

#### `$ ./run_audit.sh`

Checks third party dependencies for

* Compatible licenses
* Security vulnerabilities
* Updated versions

Example output

```shell
+==============================================================================+
|                                                                              |
|                               /$$$$$$            /$$                         |
|                              /$$__  $$          | $$                         |
|           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
|          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
|         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
|          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
|          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
|         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
|                                                          /$$  | $$           |
|                                                         |  $$$$$$/           |
|  by pyup.io                                              \______/            |
|                                                                              |
+==============================================================================+
| REPORT                                                                       |
| checked 34 packages, using default DB                                        |
+==============================================================================+
| No known security vulnerabilities found.                                     |
+==============================================================================+
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   303  100   303    0     0   1109      0 --:--:-- --:--:-- --:--:--  1105
 Name               Version    License
 python-dateutil    2.8.1      Dual License
licence checker warning
PLEASE REVIEW LICENSES LISTED ABOVE
Security audit passed
```

#### `$ ./run_static_analysis.sh`

Example output

```shell
linting python
linting bash
linting dockerfile
Static analysis passed
```

#### `$ ./run_unit_tests.sh`

Example output

```shell
collected 12 items

util/test_file.py ..                                          [100%]

===================== 12 passed in 2.29s ===========================
```
