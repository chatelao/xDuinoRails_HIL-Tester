import argparse
import serial
import subprocess
import time
import shutil
import os
import csv

# --- Configuration ---
PICO_SDK_PATH = "pico-sdk"
PICO_SERIAL_PORT = "/dev/ttyACM0"  # Adjust if your Pico uses a different port
BAUD_RATE = 115200
TIMEOUT = 10  # Seconds
EXPECTED_TOGGLES = 20

def install_arm_gcc_compiler():
    """Installs the ARM GCC compiler if it's not already present."""
    try:
        subprocess.run(["arm-none-eabi-gcc", "--version"], check=True, capture_output=True)
        print("--- ARM GCC compiler is already installed. ---")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("--- ARM GCC compiler not found. Installing... ---")
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "gcc-arm-none-eabi"], check=True)
            print("--- ARM GCC compiler installed successfully. ---")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error installing ARM GCC compiler: {e}")
            return False

def setup_pico_sdk():
    """Clones the Pico SDK if it's not already present."""
    if not os.path.exists(PICO_SDK_PATH):
        print("--- Pico SDK not found. Cloning... ---")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/raspberrypi/pico-sdk.git", PICO_SDK_PATH],
                check=True
            )
            subprocess.run(
                ["git", "submodule", "update", "--init"],
                cwd=PICO_SDK_PATH,
                check=True
            )
            print("--- Pico SDK cloned successfully. ---")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cloning Pico SDK: {e}")
            return False
    return True

def build_target(target, build_dir="build"):
    """Builds a specific firmware target using CMake and Make."""
    print(f"--- Building firmware for target: {target} ---")

    if not install_arm_gcc_compiler() or not setup_pico_sdk():
        return False

    try:
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        # Check if CMake has been run before
        if not os.path.exists(os.path.join(build_dir, "Makefile")):
            subprocess.run(["cmake", "-S", ".", "-B", build_dir], check=True)

        subprocess.run(["make", "-C", build_dir, target], check=True)
        print("--- Build successful ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building firmware: {e}")
        return False

def get_openocd_cfg(pico_id):
    """Returns the OpenOCD config file for the given Pico ID."""
    return f"cfg/pico-sut{pico_id}.cfg"

def flash_elf(firmware_elf, pico_id):
    """Flashes an ELF firmware to a specific Pico."""
    print(f"--- Flashing {firmware_elf} to Pico {pico_id} ---")
    openocd_cfg = get_openocd_cfg(pico_id)
    try:
        subprocess.run(
            [
                "openocd",
                "-f",
                openocd_cfg,
                "-c",
                f"program {firmware_elf} verify reset exit",
            ],
            check=True,
        )
        print("--- Flashing successful ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error flashing firmware: {e}")
        return False
    except FileNotFoundError:
        print("Error: openocd not found. Is it installed and in your PATH?")
        return False

def flash_uf2(firmware_uf2, pico_id):
    """Flashes a UF2 firmware to a specific Pico."""
    print(f"--- Flashing {firmware_uf2} to Pico {pico_id} ---")
    openocd_cfg = get_openocd_cfg(pico_id)

    try:
        # 1. Reset the Pico into BOOTSEL mode
        print("--- Resetting Pico to BOOTSEL mode ---")
        subprocess.run(
            [
                "openocd",
                "-f",
                openocd_cfg,
                "-c",
                "init",
                "-c",
                "rp2040.core0 arp_reset assert 0",
                "-c",
                "rp2040.core1 arp_reset assert 0",
                "-c",
                "adapter_nsrst_delay 100",
                "-c",
                "adapter_nsrst_assert",
                "-c",
                "sleep 100",
                "-c",
                "adapter_nsrst_deassert",
                "-c",
                "shutdown",
            ],
            check=True,
        )

        # Give the OS time to recognize the new device
        time.sleep(2)

        # 2. Flash with picotool
        print("--- Flashing with picotool ---")
        subprocess.run(
            ["picotool", "load", "-f", firmware_uf2],
            check=True,
        )

        # 3. Reboot the Pico
        print("--- Rebooting Pico ---")
        subprocess.run(
            ["picotool", "reboot"],
            check=True
        )

        print("--- Flashing successful ---")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during UF2 flashing process: {e}")
        return False
    except FileNotFoundError:
        print("Error: openocd or picotool not found. Are they installed and in your PATH?")
        return False

def run_blinky_test():
    """Runs the blinky test case."""
    print("--- Running Blinky Test ---")

    # 1. Build the firmware
    if not build_target("blinky", "build/test/sut/pico/blinky"):
        return False

    # 2. Flash the firmware
    firmware_elf = "build/test/sut/pico/blinky/blinky.elf"
    if not flash_elf(firmware_elf, 1):
        return False

    # 3. Verify the output
    print("--- Verifying blinking ---")
    toggle_count = 0
    try:
        with serial.Serial(PICO_SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            start_time = time.time()
            while time.time() - start_time < TIMEOUT:
                line = ser.readline().decode("utf-8").strip()
                if line == "LED toggled":
                    toggle_count += 1
                    print(f"Received toggle message {toggle_count}/{EXPECTED_TOGGLES}")
                    if toggle_count == EXPECTED_TOGGLES:
                        print("--- Verification successful ---")
                        return True
    except serial.SerialException as e:
        print(f"Error opening or reading from serial port: {e}")
        return False

    print(f"Verification failed. Received {toggle_count}/{EXPECTED_TOGGLES} messages.")
    return False

def analyze_pwm_capture(capture_file="capture.csv", expected_freq_hz=1000, tolerance=0.05):
    """Analyzes the captured PWM data to determine its frequency."""
    print(f"--- Analyzing capture file: {capture_file} ---")

    try:
        with open(capture_file, 'r') as f:
            reader = csv.reader(f)
            # Skip header
            next(reader, None)

            timestamps = []
            values = []
            for row in reader:
                # Assuming the first column is time and the second is the value
                timestamps.append(float(row[0]))
                values.append(float(row[1]))

    except (IOError, csv.Error, ValueError) as e:
        print(f"Error reading or parsing capture file: {e}")
        return False

    if not timestamps or not values:
        print("Error: No data found in capture file.")
        return False

    # Find rising edges
    rising_edges = []
    threshold = (max(values) + min(values)) / 2.0
    for i in range(1, len(values)):
        if values[i-1] < threshold and values[i] >= threshold:
            rising_edges.append(timestamps[i])

    if len(rising_edges) < 2:
        print("Error: Not enough rising edges detected to calculate frequency.")
        return False

    # Calculate periods
    periods = [rising_edges[i] - rising_edges[i-1] for i in range(1, len(rising_edges))]
    avg_period = sum(periods) / len(periods)

    if avg_period == 0:
        print("Error: Average period is zero, cannot calculate frequency.")
        return False

    frequency = 1.0 / avg_period
    print(f"Detected frequency: {frequency:.2f} Hz")

    # Check if the frequency is within tolerance
    min_freq = expected_freq_hz * (1 - tolerance)
    max_freq = expected_freq_hz * (1 + tolerance)

    if min_freq <= frequency <= max_freq:
        print(f"--- Frequency is within the expected range ({min_freq:.2f} - {max_freq:.2f} Hz) ---")
        return True
    else:
        print(f"--- Frequency is outside the expected range ---")
        return False

def run_logic_analyzer_test():
    """Runs the logic analyzer test case."""
    print("--- Running Logic Analyzer Test ---")

    # 1. Build the PWM generator firmware
    if not build_target("pico_pwm_generator"):
        return False

    # 2. Flash the PWM generator to SUT1
    pwm_firmware_elf = "build/test/pico_pwm_generator/pico_pwm_generator.elf"
    if not flash_elf(pwm_firmware_elf, 1):
        return False

    # 3. Flash the logic analyzer firmware to SUT2
    la_firmware_uf2 = "firmware/ula.uf2"
    if not flash_uf2(la_firmware_uf2, 2):
        return False

    # 4. Install sigrok-cli if not present
    try:
        subprocess.run(["sigrok-cli", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("sigrok-cli not found. Installing...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "sigrok-cli"], check=True)

    # 5. Run sigrok-cli to capture the signal
    print("--- Capturing signal with sigrok-cli ---")
    capture_file = "capture.csv"
    capture_command = [
        "sigrok-cli",
        "-d", "ols",
        "--config", "samplerate=1m",  # 1MHz sample rate is plenty for a 1kHz signal
        "--samples", "10k",
        "-O", "csv",
        "-o", capture_file,
    ]

    try:
        subprocess.run(capture_command, check=True)
        print("--- Signal captured successfully ---")
    except subprocess.CalledProcessError as e:
        print(f"Error capturing signal with sigrok-cli: {e}")
        return False

    # 6. Analyze the captured data
    return analyze_pwm_capture(capture_file)

def main():
    parser = argparse.ArgumentParser(description="HIL Test Runner")
    parser.add_argument(
        "--test",
        choices=["blinky", "logic_analyzer"],
        required=True,
        help="The test case to run.",
    )
    args = parser.parse_args()

    if args.test == "blinky":
        if run_blinky_test():
            print("--- Blinky test PASSED! ---")
            exit(0)
        else:
            print("--- Blinky test FAILED! ---")
            exit(1)
    elif args.test == "logic_analyzer":
        if run_logic_analyzer_test():
            print("--- Logic analyzer test PASSED! ---")
            exit(0)
        else:
            print("--- Logic analyzer test FAILED! ---")
            exit(1)

if __name__ == "__main__":
    main()
