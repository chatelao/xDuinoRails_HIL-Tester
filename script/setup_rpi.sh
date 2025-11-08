#!/bin/bash

# =====================================================================================
# HIL Tester Raspberry Pi Setup Script
#
# This script automates the setup of a Raspberry Pi as a HIL (Hardware-in-the-Loop)
# host controller. It installs all necessary software, including OpenOCD and the
# GitHub Actions self-hosted runner.
#
# Usage:
# 1. Make the script executable: chmod +x setup_rpi.sh
# 2. Run with sudo: ./setup_rpi.sh
# =====================================================================================

# --- Sanity Checks and Initialization ---

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if the script is run as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Please use sudo." >&2
  exit 1
fi

echo "--- HIL Tester Raspberry Pi Setup Started ---"

# --- System Update and Dependency Installation ---

echo "[1/5] Updating system packages..."
apt-get update
apt-get upgrade -y

echo "[2/5] Installing system dependencies..."
apt-get install -y \
  git \
  build-essential \
  cmake \
  libtool \
  automake \
  texinfo \
  libusb-1.0-0-dev \
  python3 \
  python3-pip \
  openocd \
  curl \
  jq

# --- Python Package Installation ---

echo "[3/5] Installing Python dependencies..."
# Get the directory where the script is located to reliably find requirements.txt
SCRIPT_DIR=$(dirname "$(realpath "$0")")
REQUIREMENTS_PATH="${SCRIPT_DIR}/requirements.txt"

if [ ! -f "${REQUIREMENTS_PATH}" ]; then
    echo "Error: Could not find requirements.txt at ${REQUIREMENTS_PATH}" >&2
    exit 1
fi

pip3 install -r "${REQUIREMENTS_PATH}"

# --- GitHub Actions Runner Setup ---

echo "[4/5] Setting up GitHub Actions self-hosted runner..."

# Create a directory for the runner
mkdir -p /actions-runner
cd /actions-runner

# Check if the runner is already installed
if [ -f "config.sh" ]; then
    echo "GitHub Actions Runner is already installed. Skipping download."
else
    # Determine system architecture
    ARCH=$(uname -m)
    RUNNER_ARCH=""
    case ${ARCH} in
        aarch64) RUNNER_ARCH="arm64";;
        armv7l) RUNNER_ARCH="arm";;
        x86_64) RUNNER_ARCH="x64";;
        *) echo "Unsupported architecture: ${ARCH}"; exit 1;;
    esac

    # Get the latest runner version
    LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name' | sed 's/v//')
    if [ -z "$LATEST_VERSION" ]; then
        echo "Failed to fetch the latest runner version. Exiting." >&2
        exit 1
    fi

    RUNNER_PACKAGE="actions-runner-linux-${RUNNER_ARCH}-${LATEST_VERSION}.tar.gz"
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${LATEST_VERSION}/${RUNNER_PACKAGE}"

    echo "Downloading runner version ${LATEST_VERSION}..."
    curl -o "${RUNNER_PACKAGE}" -L "${DOWNLOAD_URL}"

    echo "Extracting the runner..."
    tar xzf "./${RUNNER_PACKAGE}"
    rm "./${RUNNER_PACKAGE}"
fi

# --- Runner Configuration and Service Installation ---

echo "[5/5] Configuring runner and installing systemd service..."

# Check if the runner is already configured
if [ -f ".runner" ]; then
    echo "Runner is already configured. Skipping configuration."
else
    # Prompt for configuration details
    read -p "Enter the GitHub repository URL (e.g., https://github.com/user/repo): " REPO_URL
    read -p "Enter the self-hosted runner registration token: " RUNNER_TOKEN

    if [ -z "$REPO_URL" ] || [ -z "$RUNNER_TOKEN" ]; then
        echo "Repository URL and token are required. Exiting." >&2
        exit 1
    fi

    echo "Configuring the runner..."
    ./config.sh --url "${REPO_URL}" --token "${RUNNER_TOKEN}" --unattended --replace
fi

echo "Installing the runner as a systemd service..."
./svc.sh install
./svc.sh start

# --- Finalization ---
echo "-----------------------------------------------------------------"
echo "Setup Complete!"
echo "The GitHub Actions runner has been configured and started as a systemd service."
echo "You can check its status with: sudo systemctl status actions.runner.*"
echo "-----------------------------------------------------------------"

cd - > /dev/null
