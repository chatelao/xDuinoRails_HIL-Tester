#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Update and upgrade the system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required software, including jq for parsing JSON
echo "Installing required software..."
sudo apt-get install -y git python3 python3-pip openocd cmake build-essential curl jq

# Determine system architecture
ARCH=$(uname -m)
RUNNER_ARCH=""
case ${ARCH} in
    aarch64) RUNNER_ARCH="arm64";;
    armv7l) RUNNER_ARCH="arm";;
    x86_64) RUNNER_ARCH="x64";;
    *) echo "Unsupported architecture: ${ARCH}"; exit 1;;
esac

# Check if the runner is already installed
if [ -d "actions-runner" ] && [ -f "actions-runner/config.sh" ]; then
    echo "GitHub Actions Runner is already installed."
else
    # Create a directory for the GitHub Actions Runner
    mkdir -p actions-runner
    cd actions-runner

    # Get the latest runner version
    echo "Getting the latest GitHub Actions Runner version..."
    LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name' | sed 's/v//')

    # Construct the download URL
    RUNNER_PACKAGE="actions-runner-linux-${RUNNER_ARCH}-${LATEST_VERSION}.tar.gz"
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${LATEST_VERSION}/${RUNNER_PACKAGE}"

    # Download the latest runner package
    echo "Downloading the GitHub Actions Runner (version ${LATEST_VERSION})..."
    curl -o "${RUNNER_PACKAGE}" -L "${DOWNLOAD_URL}"

    # Extract the installer
    echo "Extracting the GitHub Actions Runner..."
    tar xzf "./${RUNNER_PACKAGE}"

    cd ..
fi

# Instructions for configuring the runner
echo "-----------------------------------------------------------------"
echo "The GitHub Actions Runner is ready to be configured."
echo "To configure the runner, you need to run the following command"
echo "with your repository's token:"
echo ""
echo "cd actions-runner"
echo "./config.sh --url <your-repository-url> --token <your-token>"
echo ""
echo "You can find the token in your repository's settings under"
echo "'Actions > Runners > New self-hosted runner'."
echo "-----------------------------------------------------------------"
