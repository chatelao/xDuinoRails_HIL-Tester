# HIL Tester Development Roadmap

This document outlines the development roadmap for the HIL (Hardware-in-the-Loop) tester. It is designed to guide the development from a Minimum Viable Product (MVP) to a full-featured testing system.

## 1. Minimum Viable Product (MVP)

The goal of the MVP is to get a basic HIL test running with a single SUT (Raspberry Pi Pico).

*   [x] High-Level Conceptual Design
*   [ ] **Hardware Setup:**
    *   [ ] Solder headers onto the Raspberry Pi 3 and Pico.
    *   [ ] Connect the Raspberry Pi 3 to the Pico for power and SWD programming.
*   [ ] **Host Controller (Raspberry Pi 3) Setup:**
    *   [ ] Install Raspberry Pi OS Lite (64-bit).
    *   [ ] Install and configure OpenOCD.
    *   [ ] Write a basic Python script (`run_hil_test.py`) to flash a "blinky" firmware to the Pico.
*   [ ] **SUT Firmware:**
    *   [ ] Create a simple "blinky" firmware for the Pico using the Pico SDK and CMake.
*   [ ] **Initial Test:**
    *   [ ] Manually run the Python script on the Raspberry Pi 3 to flash the Pico and verify that the LED blinks.

## 2. GitHub Actions Integration

This phase focuses on automating the MVP test using a CI/CD pipeline.

*   [ ] **Setup Self-Hosted Runner:**
    *   [ ] Configure the Raspberry Pi 3 as a self-hosted GitHub Actions runner.
    *   [ ] Assign the label `hil-tester` to the runner.
    *   [ ] Configure the runner to run as a `systemd` service for stability.
*   [ ] **Create CI Workflow (`.github/workflows/hil_test.yml`):**
    *   [ ] Define a job that runs on the `hil-tester`.
    *   [ ] Add a step to check out the repository.
    *   [ ] Add a step to build the "blinky" firmware using CMake.
    *   [ ] Add a step to execute the `run_hil_test.py` script.
*   [ ] **Result Verification:**
    *   [ ] Enhance the Python script to include a basic pass/fail condition (e.g., exit code 0 on successful flash).
    *   [ ] Trigger the workflow via a `git push` and confirm it runs successfully.

## 3. Advanced Features

This section lists future enhancements to expand the HIL tester's capabilities.

### 3.1. Multi-SUT & Communication Testing
*   [ ] **Support for Second Pico:**
    *   [ ] Update hardware connections to include a second Pico.
    *   [ ] Extend the Python orchestrator to flash firmware to both Picos.
    *   [ ] Implement a UART loopback test between the two Picos.
*   [ ] **Support for STM32F446RE:**
    *   [ ] Add hardware connections for the STM32F446RE (JTAG).
    *   [ ] Create a new OpenOCD configuration for the STM32.
    *   [ ] Implement a test involving all three SUTs.
*   [ ] **I2C Protocol Testing:**
    *   [ ] Develop firmware for an I2C master/slave test.
    *   [ ] Add I2C test cases to the Python orchestrator.
*   [ ] **SPI Protocol Testing:**
    *   [ ] Develop firmware for an SPI master/slave test.
    *   [ ] Add SPI test cases to the Python orchestrator.
*   [ ] **CAN Bus Testing:**
    *   [ ] Add CAN transceivers to the hardware setup.
    *   [ ] Develop firmware for CAN communication tests.

### 3.2. Enhanced Control and Measurement
*   [ ] **Power Consumption Monitoring:**
    *   [ ] Integrate a current sensor (e.g., INA219) into the hardware setup.
    *   [ ] Write a Python library to read current data from the sensor.
    *   [ ] Add power measurement capabilities to the test reports.
*   [ ] **GPIO Monitoring/Injection:**
    *   [ ] Implement a system to monitor GPIO pins on the SUTs.
    *   [ ] Add the ability to inject signals (e.g., simulate button presses).
*   [ ] **Analog Signal Generation & Measurement:**
    *   [ ] Add a DAC/ADC to the Raspberry Pi 3.
    *   [ ] Develop capabilities for testing analog interfaces on the SUTs.
*   [ ] **Automated Reset Control:**
    *   [ ] Implement hardware reset lines from the Raspberry Pi 3 to each SUT.
    *   [ ] Add reset control functions to the Python orchestrator.
*   [ ] **Dynamic Test Re-Configuration:**
    *   [ ] Allow tests to be configured via a JSON or YAML file instead of command-line arguments.

### 3.3. Improved Reporting & Usability
*   [ ] **Structured Test Results (Unity):**
    *   [ ] Integrate the Unity test framework into the SUT firmware.
    *   [ ] Parse Unity test results from the SUT's UART output in the Python script.
*   [ ] **HTML Test Reports:**
    *   [ ] Generate a detailed HTML report for each test run.
    *   [ ] Upload the report as a GitHub Actions artifact.
*   [ ] **Test Log Management:**
    *   [ ] Store detailed logs from OpenOCD and the SUTs for each test run.
*   [ ] **Web-Based Dashboard:**
    *   [ ] Create a simple web interface (hosted on the Pi) to view test history and SUT status.
*   [ ] **Dockerized Test Environment:**
    *   [ ] Create a Docker container with all necessary dependencies to simplify setup.

### 3.4. System Robustness & Expansion
*   [ ] **Hardware Abstraction Layer (HAL):**
    *   [ ] Refactor the Python orchestrator to use a HAL for interacting with different SUTs.
*   [ ] **Support for Additional SUTs:**
    *   [ ] Add support for another common microcontroller (e.g., ESP32).
*   [ ] **Parallel Test Execution:**
    *   [ ] If hardware allows, add the capability to run multiple, independent tests in parallel.
*   [ ] **Fault Injection Framework:**
    *   [ ] Add capabilities to intentionally introduce faults (e.g., power glitches, noisy signals) to test SUT robustness.
*   [ ] **Electrical Isolation:**
    *   [ ] Add opto-isolators between the Raspberry Pi 3 and SUTs for improved electrical safety.
