# HIL Tester Concept for Raspberry Pi 3, 2x Pico, and STM32F446RE

This document outlines the software concept for a Hardware-in-the-Loop (HIL) tester based on a Raspberry Pi 3.

## 1. High-Level Architecture

The HIL tester is composed of a central test controller (Raspberry Pi 3) and three Systems Under Test (SUTs).

*   **Raspberry Pi 3 (Host Controller):** The brain of the operation. It is responsible for:
    *   Orchestrating the entire test flow.
    *   Running the test scripts (e.g., Python).
    *   Programming the SUTs using OpenOCD via its GPIO pins.
    *   Communicating with the "verifying" SUT to retrieve test results.
    *   Reporting the final test status back to GitHub Actions.

*   **Raspberry Pi Picos & STM32F446RE (SUTs):** These are the devices whose firmware is being tested. In any given test scenario, they can be assigned different roles, such as:
    *   **Signal Generator:** Programmed to send specific data packets or generate signals (e.g., UART, SPI).
    *   **Signal Verifier:** Programmed to receive signals from another SUT and verify their correctness.

### Control and Data Flow

The following diagram illustrates the high-level architecture:

```
+---------------------------------+
|         GitHub Actions          |
+---------------------------------+
              ^
              | (Test Results)
              v
+---------------------------------+
|      Raspberry Pi 3 (Host)      |
|  - Test Orchestrator (Python)   |
|  - OpenOCD                      |
|  - GitHub Runner                |
+---------------------------------+
      |        |        |        |
(SWD) |        |        |        | (Result UART)
      v        v        v        v
+----------+ +----------+ +-------------+
|  Pico 1  | |  Pico 2  | | STM32F446RE |
|  (SUT)   | |  (SUT)   | |   (SUT)     |
+----------+ +----------+ +-------------+
      ^          ^
      |----------| (UART/SPI for testing)
      |          |
      |--------------------------| (UART/SPI for testing)
                 |
                 |---------------| (UART/SPI for testing)

```

## 2. Raspberry Pi 3 Software Stack

This section details the recommended software to be installed on the Raspberry Pi 3 to function as the host controller.

### 2.1. Operating System

*   **Recommendation:** **Raspberry Pi OS Lite (64-bit)**
*   **Reasoning:** A minimal, headless OS is ideal for a stable and resource-efficient test server. The 64-bit version ensures compatibility with the latest tools.

### 2.2. Programming/Debugging: OpenOCD

*   **Purpose:** OpenOCD (Open On-Chip Debugger) is a powerful, open-source tool that can turn the Raspberry Pi's GPIO header into a versatile SWD (Serial Wire Debug) adapter.
*   **Configuration:**
    *   OpenOCD will be configured to use the native `bcm2835-gpi` driver, which allows bit-banging the SWD protocol on the GPIO pins.
    *   Separate configuration files will be created for each SUT type (`raspberrypi-pico.cfg`, `stm32f4x.cfg`) to handle their specific SWD interfaces.
    *   The test orchestrator will invoke OpenOCD via the command line to flash the firmware binaries (`.elf` or `.uf2` files) onto the SUTs.

### 2.3. Test Orchestrator

*   **Recommendation:** **Python 3**
*   **Reasoning:** Python is an excellent choice due to its simplicity, extensive libraries for process management and serial communication (`subprocess`, `pyserial`), and its widespread use in automation.
*   **Responsibilities of the Python script:**
    1.  **Parse Arguments:** Accept parameters from the GitHub Actions workflow, such as firmware paths and the specific test to run.
    2.  **Flash SUTs:** Construct and execute OpenOCD commands to program the designated SUTs with the correct firmware.
    3.  **Manage Test Execution:** Start the test, wait for completion, and handle timeouts.
    4.  **Receive Results:** Open a serial connection to the "verifying" SUT to read the test results.
    5.  **Determine Pass/Fail:** Compare the received data with the expected outcome.
    6.  **Exit with Status Code:** Exit with `0` for a passed test and a non-zero value for a failed test, which will signal the status to the GitHub Actions runner.

### 2.4. SUT Communication Protocol

*   **Recommendation:** **UART**
*   **Reasoning:** UART is a simple, reliable, and universally supported protocol, making it perfect for sending results from the "verifying" SUT back to the Raspberry Pi 3.
*   **Implementation:**
    *   One of the Raspberry Pi 3's hardware UARTs (`/dev/ttyS0`) will be dedicated to receiving test results.
    *   The "verifying" SUT (e.g., a Pico) will be programmed to run its tests and then serialize the results into a simple format (like JSON or a custom delimited string) and send it over its UART TX pin to the Raspberry Pi 3's RX pin.
    *   The Python orchestrator will listen on the serial port for this data to determine the outcome of the test.

## 3. Automated Test Workflow

This section describes the end-to-end workflow for a single, automated test run.

1.  **Trigger:** A developer pushes a commit or opens a pull request to the firmware repository on GitHub.

2.  **Job Dispatch:** GitHub Actions queues a new workflow run. The job is configured to run on a self-hosted runner with the appropriate label (e.g., `hil-tester`).

3.  **Runner Acquires Job:** The GitHub Actions runner service on the Raspberry Pi 3 picks up the job.

4.  **Checkout and Build:** The workflow's first steps execute on the Raspberry Pi 3:
    *   The repository source code is checked out.
    *   A build script is run (e.g., `cmake` and `make`) to compile the firmware for the SUTs, producing the necessary binary files (e.g., `uart_sender.elf`, `uart_receiver.elf`).

5.  **Execute Test Orchestrator:** The workflow then calls the main Python test script, passing the paths to the firmware binaries as arguments.
    ```bash
    python3 run_hil_test.py --sender-fw build/uart_sender.elf --receiver-fw build/uart_receiver.elf
    ```

6.  **Orchestrator Flashes SUTs:** The Python script executes the following steps:
    *   It invokes OpenOCD to flash `uart_sender.elf` onto the first SUT (e.g., Pico 1).
    *   It invokes OpenOCD again to flash `uart_receiver.elf` onto the second SUT (e.g., Pico 2).

7.  **Orchestrator Runs Test:**
    *   The script opens a serial port to listen for results from the "receiver" SUT.
    *   It resets the SUTs (either via SWD or a dedicated reset pin) to start the test.
    *   The "sender" SUT executes its firmware, sending a predefined data packet over UART to the "receiver" SUT.

8.  **Result Collection and Verification:**
    *   The "receiver" SUT gets the data, compares it against an expected value, and sends a result message (e.g., `{"test": "uart_loopback", "status": "PASS"}`) back to the Raspberry Pi 3 via the dedicated UART connection.
    *   The Python script reads this message and determines the outcome.

9.  **Orchestrator Exits:** The script performs any necessary cleanup and then exits with a status code: `0` if the test passed, `1` if it failed.

10. **Job Completion:** The GitHub Actions runner reports the job's success or failure based on the script's exit code, making the result visible in the GitHub UI.

## 4. GitHub Actions Integration

To integrate the HIL tester into a CI/CD pipeline, the Raspberry Pi 3 will be configured as a self-hosted GitHub Actions runner.

### 4.1. Self-Hosted Runner Setup

1.  **Follow Official GitHub Documentation:** The most reliable setup process is to follow GitHub's official guide for adding self-hosted runners to a repository or organization. This typically involves:
    *   Navigating to `Settings > Actions > Runners` in your GitHub repository.
    *   Clicking "New self-hosted runner."
    *   Selecting "Linux" as the OS and "ARM64" as the architecture.
    *   Following the provided command-line instructions to download, configure, and run the runner agent on the Raspberry Pi 3.

2.  **Assign a Label:** During the configuration process, assign a unique label to the runner, such as `hil-tester`. This label is crucial for ensuring that HIL test jobs are routed exclusively to the Raspberry Pi 3.

3.  **Run as a Service:** For long-term stability, the runner should be configured to run as a `systemd` service, which will ensure it starts automatically on boot.

### 4.2. Example Workflow Configuration

Below is a sample GitHub Actions workflow file (`.github/workflows/hil_test.yml`) that demonstrates how to use the self-hosted runner to build and test firmware.

```yaml
name: HIL Firmware Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    # This is the critical line that targets the Raspberry Pi 3
    runs-on: hil-tester

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up build environment
      # Add steps to install your toolchain, e.g., arm-none-eabi-gcc, cmake
      run: |
        sudo apt-get update
        sudo apt-get install -y cmake gcc-arm-none-eabi

    - name: Build firmware
      run: |
        mkdir build
        cd build
        cmake ..
        make

    - name: Run HIL test
      # This step executes the test orchestrator script
      # The script's exit code determines if the step passes or fails
      run: |
        python3 run_hil_test.py \
          --sender-fw build/uart_sender.elf \
          --receiver-fw build/uart_receiver.elf
```

## 5. Hardware Connections

![Raspberry Pi GPIO Header](https://www.pi4j.com/1.2/images/p1header.png)

### 5.1. Raspberry Pi 3 Pinout Proposal

This section proposes a pinout for the Raspberry Pi 3's 26-pin GPIO header to connect the three SUTs (two Raspberry Pi Picos and one STM32F446RE). The goal is to provide a clear and reliable hardware setup for programming, debugging, and communicating with the SUTs.

| Pin # | Function                       | Function                           | Pin # |
|-------|--------------------------------|------------------------------------|-------|
| 1     | 3.3V Power                     | 5V Power                           | 2     |
| 3     | GPIO 2 (I2C1 SDA)              | 5V Power                           | 4     |
| 5     | GPIO 3 (I2C1 SCL)              | Ground                             | 6     |
| 7     | GPIO 4 / Pico 1 SWCLK          | GPIO 14 / SUT Result UART RX       | 8     |
| 9     | Ground                         | GPIO 15 / SUT Result UART TX       | 10    |
| 11    | GPIO 17 / Pico 1 SWDIO         | GPIO 18 / Pico 2 SWCLK             | 12    |
| 13    | GPIO 27 / Pico 2 SWDIO         | Ground                             | 14    |
| 15    | GPIO 22 / STM32F446RE TCK      | GPIO 23 / STM32F446RE TMS          | 16    |
| 17    | 3.3V Power                     | GPIO 24 / STM32F446RE TDO          | 18    |
| 19    | GPIO 10 / STM32F446RE TDI      | Ground                             | 20    |
| 21    | GPIO 9 (SPI0 MISO)             | GPIO 25 / Pico 1 nRST              | 22    |
| 23    | GPIO 11 (SPI0 SCLK)            | GPIO 8 / Pico 2 Reset              | 24    |
| 25    | Ground                         | GPIO 7 / STM32F446RE Reset         | 26    |
