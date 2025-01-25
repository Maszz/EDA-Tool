#!/bin/bash

# Define the environment name and requirements file location
ENV_NAME="env"
REQUIREMENTS="requirements.txt"

# Check if the script is being sourced or not
# Allow direct execution only for 'install' command
if [[ "${BASH_SOURCE[0]}" == "${0}" && "$1" != "install" ]]; then
    echo "This command must be sourced to function correctly."
    echo "Usage: source ${0} [activate|deactivate]"
    exit 1
fi

function create_env() {
    if [ -d "$ENV_NAME" ]; then
        echo "Virtual environment $ENV_NAME already exists."
    else
        echo "Creating virtual environment..."
        python -m venv $ENV_NAME
        echo "Environment created."
        install_dependencies
    fi
}

function install_dependencies() {
    echo "Installing dependencies from $REQUIREMENTS..."
    if [[ "$OSTYPE" == "win32" || "$OSTYPE" == "msys" ]]; then
        source $ENV_NAME/Scripts/activate
    else
        source $ENV_NAME/bin/activate
    fi
    pip install -r $REQUIREMENTS
    echo "Dependencies installed."
}

function activate_env() {
    if [ ! -d "$ENV_NAME" ]; then
        echo "Virtual environment not found. Please run './env.sh install' to create and install the environment."
    else
        echo "Activating virtual environment..."
        if [[ "$OSTYPE" == "win32" || "$OSTYPE" == "msys" ]]; then
            source $ENV_NAME/Scripts/activate
        else
            source $ENV_NAME/bin/activate
        fi
    fi
}

function deactivate_env() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "No active virtual environment."
    else
        echo "Deactivating virtual environment..."
        deactivate
    fi
}

# Execute or source command based on input
case "$1" in 
    install)
        create_env
        ;;
    activate)
        activate_env
        ;;
    deactivate)
        deactivate_env
        ;;
    *)
        echo "Usage: source ${0} [activate|deactivate] or . ${0} [activate|deactivate] or ${0} install"
        ;;
esac