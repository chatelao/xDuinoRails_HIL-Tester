# 100 Improvements for the HIL Tester Implementation

This document outlines 100 proposed improvements for the current Hardware-in-the-Loop (HIL) tester implementation. The improvements are categorized to facilitate prioritization and planning.

## 1. Hardware & Electrical Architecture

1.  **Migrate to `linuxgpiod`:** Replace the deprecated `bcm2835gpio` OpenOCD driver with `linuxgpiod` for better compatibility with modern kernels.
2.  **Add Level Shifters:** Although Picos are 3.3V, adding buffers protects the Pi's GPIOs from accidental shorts or voltage spikes.
3.  **Implement Power Switching:** Add a relay or MOSFET circuit to programmatically power cycle the SUTs to recover from hard hangs.
4.  **Design a Custom HAT:** Move from jumper wires to a custom PCB (HAT) for the Raspberry Pi to improve reliability and signal integrity.
5.  **Add ESD Protection:** Install TVS diodes on all exposed connectors to protect against electrostatic discharge.
6.  **Add Current Limiting:** Place series resistors (e.g., 330Ω) on all signal lines between the Host and SUTs.
7.  **Dedicated Ground Plane:** Ensure a solid common ground connection between all devices to minimize noise.
8.  **Standardize Connectors:** Use keyed connectors (like JST-XH) instead of DuPont headers to prevent reverse polarity connections.
9.  **Add Status LEDs:** Include LEDs on the HAT to indicate 3.3V/5V power presence and SUT activity.
10. **Test Points:** specific test points for oscilloscope probes to verify signal integrity during debugging.
11. **Use Shielded Cabling:** For UART and high-speed signals (SWD), use shielded cables if the length exceeds 10cm.
12. **Integrate Current Measurement:** Add a current shunt monitor (e.g., INA219) to measure SUT power consumption during tests.
13. **Add Reset Buttons:** Include physical reset buttons on the HAT for manual intervention.
14. **Breakout Unused Pins:** Route unused Pi GPIOs to a header for future expansion.
15. **Label Everything:** Clearly label all connectors and test points on the hardware setup.
16. **Validate SWD Speed:** Scientifically tune the `adapter_speed` (currently magic numbers) based on cable length and capacitance.
17. **Power Supply Filtering:** Add bulk capacitors near the SUT power connectors to prevent brownouts during high load.
18. **Thermal Management:** Add a heatsink or fan to the Raspberry Pi if running long compile jobs.
19. **Add EEPROM to HAT:** Follow the Raspberry Pi HAT specification to include an ID EEPROM for auto-configuration.

## 2. Firmware Development (SUTs)

20. **Use CMake Presets:** Implement CMake presets to standardize build configurations (Debug, Release, Test).
21. **Enable Compiler Warnings:** Set `-Wall -Wextra -Werror` to catch bugs early.
22. **Static Analysis:** Integrate `clang-tidy` or `cppcheck` into the build process.
23. **Consistent Formatting:** Enforce code style using `clang-format`.
24. **Watchdog Timer:** Enable the hardware watchdog on SUTs to auto-reset if firmware hangs.
25. **Heartbeat LED:** Implement a non-blocking heartbeat blink pattern to visually verify the SUT main loop is running.
26. **Software Reset Command:** Implement a UART command to trigger a software reset.
27. **Health Check Command:** Add a `?` or `status` UART command that returns firmware version and uptime.
28. **Version Embedding:** Embed the Git commit hash into the firmware binary during build.
29. **Shared Libraries:** Extract common code (UART drivers, protocol parsers) into a `common` submodule.
30. **Unit Testing:** Use Unity/CMock to unit test firmware logic on the host (x86) before flashing.
31. **Binary Output:** Generate `.bin` and `.hex` files alongside `.elf` and `.uf2` for flexibility.
32. **Optimize for Size:** Use `-Os` for release builds to save flash space.
33. **Bootloader Protection:** Ensure the test firmware doesn't overwrite the bootloader area if using a custom bootloader.
34. **Crash Dumps:** Implement a mechanism to dump register state to UART upon a HardFault.
35. **Standardize Pin Definitions:** Use a shared header file or CMake definitions for pin assignments across all SUTs.
36. **Parameterize Builds:** Allow injecting configuration (like baud rate) via CMake variables.

## 3. Host Software (Orchestrator)

37. **Modular Architecture:** Refactor `run_hil_test.py` into classes (`DeviceManager`, `FlashTool`, `TestRunner`).
38. **Configuration File:** Move hardcoded constants (pins, paths, timeouts) to a `config.yaml` or `.env` file.
39. **Dependency Management:** Create a strict `requirements.txt` with pinned versions.
40. **Virtual Environment:** Enforce the use of a Python virtual environment (`venv`) to avoid polluting the system.
41. **Robust Logging:** Replace `print()` with the `logging` module; log to file and console with timestamps.
42. **Async I/O:** Use `asyncio` to handle multiple SUTs concurrently (e.g., one sending, one receiving).
43. **Type Hinting:** Add Python type hints (PEP 484) to all functions.
44. **Linting & Formatting:** Enforce `black`, `isort`, and `pylint`/`flake8`.
45. **Unit Tests:** Write `pytest` unit tests for the orchestrator logic itself (mocking serial/subprocess).
46. **Retry Logic:** Implement retries with exponential backoff for flashing and serial connection attempts.
47. **Dynamic Port Discovery:** Identify SUTs by USB serial number or physical port path (using `pyudev`) instead of hardcoded `/dev/ttyACM0`.
48. **Structured Results:** Output test results in JUnit XML format for easy integration with CI systems.
49. **Pandas for Analysis:** Use `pandas` for more robust CSV processing and data analysis.
50. **Matplotlib Integration:** Generate and save plots of captured signals for manual review.
51. **Timeout Handling:** Ensure *every* `subprocess.run` call has a `timeout` parameter.
52. **Clean Up:** Implement a cleanup context manager to ensure serial ports are closed and temp files removed on failure.
53. **Argparse Subcommands:** Structure the CLI with subcommands (e.g., `hil.py flash`, `hil.py test`, `hil.py clean`).
54. **Dry Run Mode:** Add a `--dry-run` flag to simulate actions without touching hardware.
55. **Error Codes:** Define specific exit codes for different failure types (Build fail, Flash fail, Test fail).
56. **System Health Check:** Log Pi CPU temperature and load before running tests.
57. **Picotool Parsing:** Parse `picotool info` output to verify the correct device is connected before flashing.
58. **Signal Processing:** Apply software filters (low-pass, median) to logic analyzer data to reduce noise.
59. **Interactive Mode:** Add a mode to manually send UART commands for debugging.

## 4. CI/CD Pipeline (GitHub Actions)

60. **Split Build and Test:** Separate the workflow into a "Build" job (on GitHub cloud runners) and a "Test" job (on the Pi).
61. **Cross-Compilation:** Cross-compile firmware on x86 ubuntu runners to save time and reduce load on the Pi.
62. **Artifact Management:** Upload compiled firmware as artifacts from the Build job; download them in the Test job.
63. **Caching:** Cache `pico-sdk` and pip dependencies to speed up builds.
64. **Matrix Testing:** Use a build matrix to test against different configurations or firmware versions.
65. **Test Reporting:** Use a GitHub Action to publish the JUnit XML test results to the PR.
66. **Artifact Archival:** Archive captured CSVs and plots on failure for debugging.
67. **Workflow Dispatch:** Enable `workflow_dispatch` to manually trigger HIL tests from the UI.
68. **Timeout Safety:** Set a global timeout for the job to prevent a hung Pi from blocking the runner indefinitely.
69. **Concurrency Groups:** Use concurrency groups to prevent multiple jobs from trying to access the hardware simultaneously.
70. **Notification:** Send Slack/Email notifications on HIL test failure.
71. **Clean Workspace:** Ensure `git clean -fdx` runs before/after jobs to prevent state leakage.
72. **Linting Job:** Add a separate job for checking code style (Python and C).

## 5. System Administration & Security

73. **Non-Root Runner:** Configure the GitHub Actions runner to run as a dedicated user, not root.
74. **Udev Rules:** Create `udev` rules to grant non-root access to USB devices (OpenOCD/Picotool).
75. **Persistent Device Naming:** Use `udev` rules to create symlinks like `/dev/pico_sut1` based on USB topology.
76. **Ansible Provisioning:** Replace `setup_rpi.sh` with an Ansible playbook for idempotent, maintainable configuration.
77. **Disable Serial Console:** Ensure the Pi's serial console is disabled in `raspi-config` to free up the UART.
78. **Static IP:** Configure a static IP or DHCP reservation for the Pi to ensure consistent SSH access.
79. **SSH Hardening:** Disable password login and use SSH keys only.
80. **Log Rotation:** Configure `logrotate` for the runner and application logs.
81. **Dependency Isolation:** Install Python tools in a virtual environment, not globally.
82. **Watchdog for Runner:** Set up a cron job or systemd timer to check if the runner service is healthy.
83. **Secret Management:** Do not store tokens in scripts; pass them as environment variables or secrets.

## 6. Documentation

84. **Wiring Diagram:** Create a professional schematic or Fritzing diagram of the connections.
85. **API Documentation:** Use Sphinx to generate documentation for the Python orchestrator.
86. **Troubleshooting Guide:** Compile a list of common errors and solutions (e.g., "OpenOCD verification failed").
87. **Theory of Operation:** Document *why* the tests are designed this way, not just *how* to run them.
88. **BOM:** List the exact Bill of Materials (cables, resistors, Pi model) required to replicate the setup.
89. **Changelog:** Maintain a `CHANGELOG.md` following "Keep a Changelog" conventions.
90. **Example PR:** specific example of a "good" PR that includes tests.
91. **Quick Start:** A "Zero to Hero" guide for a new developer to run their first test.

## 7. Testing Strategy

92. **Corner Case Testing:** Add tests for edge cases (max data length, invalid characters).
93. **Long-Running Tests:** Implement a "soak test" that runs for hours to check for memory leaks or thermal issues.
94. **Fuzz Testing:** Send random garbage data to the SUT UART to ensure it doesn't crash.
95. **Interruption Testing:** Simulate power loss or reset during a test (if hardware allows).
96. **Performance Benchmarking:** Measure and track the round-trip time of signals.
97. **STM32 Integration:** Actually implement and enable the tests for the STM32F446RE.
98. **Mock Hardware:** Create a "software-only" mode where the SUTs are mocked, allowing logic verification without hardware.
99. **Regression Suite:** Define a core set of tests that must pass before any merge.
100. **Visual Verification:** Use the logic analyzer captures to automatically verify pulse widths and timing, not just frequency.
