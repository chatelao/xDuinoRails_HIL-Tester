# 100 Improvements for the HIL Tester Implementation

This document outlines 100 proposed improvements for the current Hardware-in-the-Loop (HIL) tester implementation. The improvements are categorized to facilitate prioritization and planning.

## 1. Hardware & Electrical Architecture

- [ ] **Migrate to `linuxgpiod`:** Replace the deprecated `bcm2835gpio` OpenOCD driver with `linuxgpiod` for better compatibility with modern kernels.
- [ ] **Add Level Shifters:** Although Picos are 3.3V, adding buffers protects the Pi's GPIOs from accidental shorts or voltage spikes.
- [ ] **Implement Power Switching:** Add a relay or MOSFET circuit to programmatically power cycle the SUTs to recover from hard hangs.
- [ ] **Design a Custom HAT:** Move from jumper wires to a custom PCB (HAT) for the Raspberry Pi to improve reliability and signal integrity.
- [ ] **Add ESD Protection:** Install TVS diodes on all exposed connectors to protect against electrostatic discharge.
- [ ] **Add Current Limiting:** Place series resistors (e.g., 330Ω) on all signal lines between the Host and SUTs.
- [ ] **Dedicated Ground Plane:** Ensure a solid common ground connection between all devices to minimize noise.
- [ ] **Standardize Connectors:** Use keyed connectors (like JST-XH) instead of DuPont headers to prevent reverse polarity connections.
- [ ] **Add Status LEDs:** Include LEDs on the HAT to indicate 3.3V/5V power presence and SUT activity.
- [ ] **Test Points:** specific test points for oscilloscope probes to verify signal integrity during debugging.
- [ ] **Use Shielded Cabling:** For UART and high-speed signals (SWD), use shielded cables if the length exceeds 10cm.
- [ ] **Integrate Current Measurement:** Add a current shunt monitor (e.g., INA219) to measure SUT power consumption during tests.
- [ ] **Add Reset Buttons:** Include physical reset buttons on the HAT for manual intervention.
- [ ] **Breakout Unused Pins:** Route unused Pi GPIOs to a header for future expansion.
- [ ] **Label Everything:** Clearly label all connectors and test points on the hardware setup.
- [ ] **Validate SWD Speed:** Scientifically tune the `adapter_speed` (currently magic numbers) based on cable length and capacitance.
- [ ] **Power Supply Filtering:** Add bulk capacitors near the SUT power connectors to prevent brownouts during high load.
- [ ] **Thermal Management:** Add a heatsink or fan to the Raspberry Pi if running long compile jobs.
- [ ] **Add EEPROM to HAT:** Follow the Raspberry Pi HAT specification to include an ID EEPROM for auto-configuration.

## 2. Firmware Development (SUTs)

- [ ] **Use CMake Presets:** Implement CMake presets to standardize build configurations (Debug, Release, Test).
- [ ] **Enable Compiler Warnings:** Set `-Wall -Wextra -Werror` to catch bugs early.
- [ ] **Static Analysis:** Integrate `clang-tidy` or `cppcheck` into the build process.
- [ ] **Consistent Formatting:** Enforce code style using `clang-format`.
- [ ] **Watchdog Timer:** Enable the hardware watchdog on SUTs to auto-reset if firmware hangs.
- [ ] **Heartbeat LED:** Implement a non-blocking heartbeat blink pattern to visually verify the SUT main loop is running.
- [ ] **Software Reset Command:** Implement a UART command to trigger a software reset.
- [ ] **Health Check Command:** Add a `?` or `status` UART command that returns firmware version and uptime.
- [ ] **Version Embedding:** Embed the Git commit hash into the firmware binary during build.
- [ ] **Shared Libraries:** Extract common code (UART drivers, protocol parsers) into a `common` submodule.
- [ ] **Unit Testing:** Use Unity/CMock to unit test firmware logic on the host (x86) before flashing.
- [ ] **Binary Output:** Generate `.bin` and `.hex` files alongside `.elf` and `.uf2` for flexibility.
- [ ] **Optimize for Size:** Use `-Os` for release builds to save flash space.
- [ ] **Bootloader Protection:** Ensure the test firmware doesn't overwrite the bootloader area if using a custom bootloader.
- [ ] **Crash Dumps:** Implement a mechanism to dump register state to UART upon a HardFault.
- [ ] **Standardize Pin Definitions:** Use a shared header file or CMake definitions for pin assignments across all SUTs.
- [ ] **Parameterize Builds:** Allow injecting configuration (like baud rate) via CMake variables.

## 3. Host Software (Orchestrator)

- [ ] **Modular Architecture:** Refactor `run_hil_test.py` into classes (`DeviceManager`, `FlashTool`, `TestRunner`).
- [ ] **Configuration File:** Move hardcoded constants (pins, paths, timeouts) to a `config.yaml` or `.env` file.
- [ ] **Dependency Management:** Create a strict `requirements.txt` with pinned versions.
- [ ] **Virtual Environment:** Enforce the use of a Python virtual environment (`venv`) to avoid polluting the system.
- [ ] **Robust Logging:** Replace `print()` with the `logging` module; log to file and console with timestamps.
- [ ] **Async I/O:** Use `asyncio` to handle multiple SUTs concurrently (e.g., one sending, one receiving).
- [ ] **Type Hinting:** Add Python type hints (PEP 484) to all functions.
- [ ] **Linting & Formatting:** Enforce `black`, `isort`, and `pylint`/`flake8`.
- [ ] **Unit Tests:** Write `pytest` unit tests for the orchestrator logic itself (mocking serial/subprocess).
- [ ] **Retry Logic:** Implement retries with exponential backoff for flashing and serial connection attempts.
- [ ] **Dynamic Port Discovery:** Identify SUTs by USB serial number or physical port path (using `pyudev`) instead of hardcoded `/dev/ttyACM0`.
- [ ] **Structured Results:** Output test results in JUnit XML format for easy integration with CI systems.
- [ ] **Pandas for Analysis:** Use `pandas` for more robust CSV processing and data analysis.
- [ ] **Matplotlib Integration:** Generate and save plots of captured signals for manual review.
- [ ] **Timeout Handling:** Ensure *every* `subprocess.run` call has a `timeout` parameter.
- [ ] **Clean Up:** Implement a cleanup context manager to ensure serial ports are closed and temp files removed on failure.
- [ ] **Argparse Subcommands:** Structure the CLI with subcommands (e.g., `hil.py flash`, `hil.py test`, `hil.py clean`).
- [ ] **Dry Run Mode:** Add a `--dry-run` flag to simulate actions without touching hardware.
- [ ] **Error Codes:** Define specific exit codes for different failure types (Build fail, Flash fail, Test fail).
- [ ] **System Health Check:** Log Pi CPU temperature and load before running tests.
- [ ] **Picotool Parsing:** Parse `picotool info` output to verify the correct device is connected before flashing.
- [ ] **Signal Processing:** Apply software filters (low-pass, median) to logic analyzer data to reduce noise.
- [ ] **Interactive Mode:** Add a mode to manually send UART commands for debugging.

## 4. CI/CD Pipeline (GitHub Actions)

- [ ] **Split Build and Test:** Separate the workflow into a "Build" job (on GitHub cloud runners) and a "Test" job (on the Pi).
- [ ] **Cross-Compilation:** Cross-compile firmware on x86 ubuntu runners to save time and reduce load on the Pi.
- [ ] **Artifact Management:** Upload compiled firmware as artifacts from the Build job; download them in the Test job.
- [ ] **Caching:** Cache `pico-sdk` and pip dependencies to speed up builds.
- [ ] **Matrix Testing:** Use a build matrix to test against different configurations or firmware versions.
- [ ] **Test Reporting:** Use a GitHub Action to publish the JUnit XML test results to the PR.
- [ ] **Artifact Archival:** Archive captured CSVs and plots on failure for debugging.
- [ ] **Workflow Dispatch:** Enable `workflow_dispatch` to manually trigger HIL tests from the UI.
- [ ] **Timeout Safety:** Set a global timeout for the job to prevent a hung Pi from blocking the runner indefinitely.
- [ ] **Concurrency Groups:** Use concurrency groups to prevent multiple jobs from trying to access the hardware simultaneously.
- [ ] **Notification:** Send Slack/Email notifications on HIL test failure.
- [ ] **Clean Workspace:** Ensure `git clean -fdx` runs before/after jobs to prevent state leakage.
- [ ] **Linting Job:** Add a separate job for checking code style (Python and C).

## 5. System Administration & Security

- [ ] **Non-Root Runner:** Configure the GitHub Actions runner to run as a dedicated user, not root.
- [ ] **Udev Rules:** Create `udev` rules to grant non-root access to USB devices (OpenOCD/Picotool).
- [ ] **Persistent Device Naming:** Use `udev` rules to create symlinks like `/dev/pico_sut1` based on USB topology.
- [ ] **Ansible Provisioning:** Replace `setup_rpi.sh` with an Ansible playbook for idempotent, maintainable configuration.
- [ ] **Disable Serial Console:** Ensure the Pi's serial console is disabled in `raspi-config` to free up the UART.
- [ ] **Static IP:** Configure a static IP or DHCP reservation for the Pi to ensure consistent SSH access.
- [ ] **SSH Hardening:** Disable password login and use SSH keys only.
- [ ] **Log Rotation:** Configure `logrotate` for the runner and application logs.
- [ ] **Dependency Isolation:** Install Python tools in a virtual environment, not globally.
- [ ] **Watchdog for Runner:** Set up a cron job or systemd timer to check if the runner service is healthy.
- [ ] **Secret Management:** Do not store tokens in scripts; pass them as environment variables or secrets.

## 6. Documentation

- [ ] **Wiring Diagram:** Create a professional schematic or Fritzing diagram of the connections.
- [ ] **API Documentation:** Use Sphinx to generate documentation for the Python orchestrator.
- [ ] **Troubleshooting Guide:** Compile a list of common errors and solutions (e.g., "OpenOCD verification failed").
- [ ] **Theory of Operation:** Document *why* the tests are designed this way, not just *how* to run them.
- [ ] **BOM:** List the exact Bill of Materials (cables, resistors, Pi model) required to replicate the setup.
- [ ] **Changelog:** Maintain a `CHANGELOG.md` following "Keep a Changelog" conventions.
- [ ] **Example PR:** specific example of a "good" PR that includes tests.
- [ ] **Quick Start:** A "Zero to Hero" guide for a new developer to run their first test.

## 7. Testing Strategy

- [ ] **Corner Case Testing:** Add tests for edge cases (max data length, invalid characters).
- [ ] **Long-Running Tests:** Implement a "soak test" that runs for hours to check for memory leaks or thermal issues.
- [ ] **Fuzz Testing:** Send random garbage data to the SUT UART to ensure it doesn't crash.
- [ ] **Interruption Testing:** Simulate power loss or reset during a test (if hardware allows).
- [ ] **Performance Benchmarking:** Measure and track the round-trip time of signals.
- [ ] **STM32 Integration:** Actually implement and enable the tests for the STM32F446RE.
- [ ] **Mock Hardware:** Create a "software-only" mode where the SUTs are mocked, allowing logic verification without hardware.
- [ ] **Regression Suite:** Define a core set of tests that must pass before any merge.
- [ ] **Visual Verification:** Use the logic analyzer captures to automatically verify pulse widths and timing, not just frequency.
