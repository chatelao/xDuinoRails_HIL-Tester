import serial
import subprocess
import time
import argparse
import re
import shutil

# --- Configuration ---
FIRMWARE_ELF = "build/test/pico_test.elf"
PICO_SERIAL_PORT = "/dev/ttyACM0"  # Adjust if your Pico uses a different port
BAUD_RATE = 115200
TIMEOUT = 15  # Seconds

def build_firmware():
    """Builds the SUT firmware using CMake and Make."""
    print("--- Building SUT firmware ---")
    try:
        # Clean the build directory to ensure a fresh build
        if shutil.os.path.exists("build"):
            shutil.rmtree("build")

        # Explicitly specify the build directory and source directory for CMake
        subprocess.run(["cmake", "-B", "build", "-S", "."], check=True)
        subprocess.run(["make", "-C", "build"], check=True)
        print("--- Build successful ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building firmware: {e}")
        return False

def flash_firmware(firmware_path):
    """Flashes the firmware to the Pico using OpenOCD."""
    print(f"--- Flashing firmware: {firmware_path} ---")
    try:
        subprocess.run(
            [
                "openocd",
                "-f",
                "interface/raspberrypi-swd.cfg",
                "-f",
                "target/rp2040.cfg",
                "-c",
                f"program {firmware_path} verify reset exit",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("--- Flashing successful ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error flashing firmware: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False
    except FileNotFoundError:
        print("Error: openocd not found. Is it installed and in your PATH?")
        return False

def verify_unity_test():
    """Verifies the test by parsing Unity's output from the UART."""
    print("--- Verifying Unity test results ---")
    try:
        with serial.Serial(PICO_SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            lines = []
            start_time = time.time()
            while time.time() - start_time < TIMEOUT:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"UART> {line}")
                    lines.append(line)
                    # Check for the Unity summary line
                    match = re.search(r"(\d+)\s+Tests,\s+(\d+)\s+Failures,\s+(\d+)\s+Ignored", line)
                    if match:
                        tests = int(match.group(1))
                        failures = int(match.group(2))
                        ignored = int(match.group(3))

                        if failures == 0 and ignored == 0 and tests > 0:
                            print("--- Unity test successful ---")
                            return True
                        else:
                            print(f"--- Unity test failed: {failures} failures, {ignored} ignored ---")
                            return False

            print("--- Verification failed: Timed out waiting for Unity summary ---")
            print("Received lines:")
            for l in lines:
                print(l)
            return False

    except serial.SerialException as e:
        print(f"Error opening or reading from serial port: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run HIL test for Raspberry Pi Pico.")
    parser.add_argument("--skip-build", action="store_true", help="Skip the build step.")
    parser.add_argument("--firmware", default=FIRMWARE_ELF, help="Path to the firmware .elf file.")
    args = parser.parse_args()

    if not args.skip_build:
        if not build_firmware():
            exit(1)

    if not flash_firmware(args.firmware):
        exit(1)

    # Add a small delay for the SUT to boot and start running tests
    time.sleep(2)

    if not verify_unity_test():
        exit(1)

    print("--- HIL test completed successfully! ---")
    exit(0)

if __name__ == "__main__":
    main()
