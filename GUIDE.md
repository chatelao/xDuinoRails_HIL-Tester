# HIL Tester Guide

This guide provides a comprehensive overview of the Hardware-in-the-Loop (HIL) tester, including setup, usage, and hardware recommendations.

## 1. Introduction

The HIL tester is a powerful tool for automating firmware testing on real hardware. It uses a Raspberry Pi 3 as a host controller to program and monitor three Systems Under Test (SUTs): two Raspberry Pi Picos and one STM32F446RE. This allows for robust, repeatable testing of firmware in a CI/CD environment.

## 2. Getting Started

This section walks you through the initial setup of the HIL tester.

### 2.1. Hardware Setup

1.  **Raspberry Pi 3:** The host controller.
2.  **SUTs:** 2x Raspberry Pi Pico, 1x STM32F446RE.
3.  **Connections:** Connect the SUTs to the Raspberry Pi 3's GPIO header as described in `HIL_TESTER_CONCEPT.md`.

### 2.2. Software Setup

The software setup is automated via a setup script.

1.  **Install Raspberry Pi OS:** Start with a fresh installation of Raspberry Pi OS Lite (64-bit).
2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```
3.  **Run the Setup Script:**
    ```bash
    chmod +x script/setup_rpi.sh
    sudo ./script/setup_rpi.sh
    ```
    The script will install all necessary software, including OpenOCD, and configure the Raspberry Pi as a self-hosted GitHub Actions runner.

## 3. Running Tests

The HIL tests are orchestrated by a Python script.

1.  **Build the Firmware:**
    ```bash
    cmake -B build -S .
    make -C build
    ```
2.  **Run the Test Script:**
    ```bash
    python3 script/run_hil_test.py
    ```
    The script will flash the firmware to the SUTs and monitor the test execution, reporting a pass or fail status.

## 4. CI/CD Integration

The HIL tester is designed to be integrated into a CI/CD pipeline using GitHub Actions.

-   **Self-Hosted Runner:** The Raspberry Pi 3 is configured as a self-hosted runner with the label `hil-tester`.
-   **Workflow:** The `.github/workflows/hil_test.yml` file defines the CI workflow. It builds the firmware and then runs the HIL test on the `hil-tester`.

## 5. Troubleshooting

-   **Flashing Fails:**
    -   Ensure OpenOCD is installed and in your PATH.
    -   Check the SWD connections between the Raspberry Pi and the SUT.
-   **Serial Communication Errors:**
    -   Verify the serial port (`/dev/ttyACM0`) is correct.
    -   Ensure the baud rate in the script matches the SUT's firmware.

## 6. Hardware Recommendations

To improve the robustness and capabilities of the HIL tester, consider the following hardware upgrades:

### 6.1. Custom HAT

A custom Hardware Attached on Top (HAT) for the Raspberry Pi would provide a more reliable and professional setup than jumper wires. The HAT should include:

-   **Dedicated SUT Sockets:** Sockets for the Picos and the STM32F446RE.
-   **Level Shifters:** To protect the Raspberry Pi's GPIOs from voltage mismatches.
-   **Power Management:** A dedicated power supply for the SUTs.

### 6.2. Improved Power Supply

A high-quality, stable power supply is crucial for reliable testing. A 5V, 3A power supply is recommended.

### 6.3. Electrical Isolation

For enhanced safety and to prevent ground loops, consider adding opto-isolators between the Raspberry Pi and the SUTs.
