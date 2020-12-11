#!/usr/bin/env bash

IMAGE_NAME=${CI_IMAGE:-"docker.pkg.github.com/rainthief/robot-test-libraries/ci_support_image:0.0.1"}
CI=${CI:-"false"}
PYTHONPATH="$(pwd)"
export PYTHONPATH


_pushd(){
    command pushd "$@" > /dev/null
}

_popd(){
    command popd > /dev/null
}

exec_in_container() {

    CONT_USER=$(id -u):$(id -g)
    OPTS="-it --init"

    if [ "$CI" == "true" ]; then
        CONT_USER=0
        docker login "$DOCKER_REG" -u "$DOCKER_USER" -p "$DOCKER_PASS"
    fi

    if ! docker pull "$IMAGE_NAME"; then
        _pushd "${PROJECT_ROOT}"
        docker build --pull -t "$IMAGE_NAME" -f ./scripts/Dockerfile .
        exitonfail $? "Docker build"
        _popd
    fi

    if [ "$CI" == "true" ]; then
        CONT_USER=0
        OPTS="-t"
    fi

    CONT_NAME=$(basename "$IMAGE_NAME" | sed -r 's/:(.*)//' )

    docker run --rm $OPTS -u="$CONT_USER" --name "$CONT_NAME" \
        -v "$PROJECT_ROOT/:/usr/app/" \
        -e "CI=$CI" \
        -e "PYTHONPATH=/usr/app" \
        --network=host \
        "$IMAGE_NAME" "$@"
}

exitonfail() {
    if [ "$1" -ne "0" ]
    then
        echo_danger "$2 failed"
        exit 1
    fi
}

warnonfail() {
    if [ "$1" -ne "0" ] && [ "$CI" != "true" ]
    then
        echo_warning "$2 warning"
    fi
}

echo_colour() {
    colour=$2
    no_colour='\033[0m'
    echo -e "${colour}$1${no_colour}"
}

echo_warning(){
    yellow='\033[0;33;1m'
    echo_colour "$1" "${yellow}"
}

echo_success(){
    green='\033[0;32;1m'
    echo_colour "$1" "${green}"
}

echo_danger(){
    red='\033[0;31;1m'
    echo_colour "$1" "${red}"
}

echo_info(){
  cyan='\033[0;36;1m'
  echo_colour "$1" "${cyan}"
}
