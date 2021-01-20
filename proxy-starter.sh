#!/bin/bash

################################################################################
# Help                                                                         #
################################################################################
Help()
{
   # Display Help
   echo "Starts the playback-proxy server via uvicorn"
   echo
   echo "Syntax: ./proxy-starter.sh [-u|m|r|e|a|p|h]"
   echo "options:"
   echo "u     Specify path to uvicorn"
   echo "m     Specify mode PROXY|RECORD|PLAYBACK"
   echo "r     Specify recording name"
   echo "e     Specify env file path"
   echo "a     Specify host"
   echo "p     Specify port"
   echo "h     Print this Help."
   echo
}

################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

while getopts "u:m:r:e:a:p:h" opt; do
    case ${opt} in
        u) UVICORN_PATH=${OPTARG} ;;
        m) MODE=${OPTARG} ;;
        r) RECORDING=${OPTARG} ;;
        e) ENV_PATH=${OPTARG} ;;
        a) HOST=${OPTARG} ;;
        p) PORT=${OPTARG} ;;
        h) Help
           exit ;;
        \?) echo "Error: Invalid option"
            exit;;
    esac
done

if [ -z ${UVICORN_PATH+x} ];
then
    echo "UVICORN_PATH -u is not set"
    exit 1
fi

if [ -z ${ENV_PATH+x} ];
then
    echo "ENV_PATH -e is not set"
    exit 1
fi

if [ -z ${HOST+x} ];
then
    echo "HOST -a is not set"
    exit 1
fi

if [ -z ${PORT+x} ];
then
    echo "PORT -p is not set"
    exit 1
fi

if [ -n "$MODE" ] && [ -n "${RECORDING}" ]
then
    echo "Setting ${MODE} mode, ${RECORDING} record name to env file at ${ENV_PATH}"
    sed -i '' -E "s|MODE=\"(..*)\"|MODE=\"${MODE}\"|g" "${ENV_PATH}"
    sed -i '' -E "s|RECORDING=\"(..*)\"|RECORDING=\"${RECORDING}\"|g" "${ENV_PATH}"
fi

$UVICORN_PATH --app-dir ./playback-proxy/ main:app --host "${HOST}" --port "${PORT}" --log-level info --no-access-log --env-file "${ENV_PATH}"