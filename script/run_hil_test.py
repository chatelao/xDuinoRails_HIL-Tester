import argparse
import subprocess
import sys
import serial
import time

def flash_firmware(firmware_path):
    """Flashes the firmware to the Pico using OpenOCD."""
    print(f"Flashing firmware: {firmware_path}")
    try:
        subprocess.run(
            ["openocd", "-f", "cfg/pico1.cfg", "-c", f"program {firmware_path} verify reset exit"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Firmware flashed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print("Error flashing firmware:")
        print(e.stdout)
        print(e.stderr)
        return False

def run_tests(serial_port):
    """Monitors the serial port for Unity test results."""
    print(f"Monitoring serial port: {serial_port}")
    try:
        with serial.Serial(serial_port, 115200, timeout=10) as ser:
            output = ser.read_until(b"UNITY_END").decode("utf-8")
            print("--- Test Output ---")
            print(output)
            print("-------------------")

            if "FAIL" in output or "IGNORE" in output:
                print("Tests failed or were ignored.")
                return False
            elif "OK" in output:
                print("All tests passed.")
                return True
            else:
                print("Could not determine test result.")
                return False
    except serial.SerialException as e:
        print(f"Error opening or reading from serial port: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run HIL tests on a Raspberry Pi Pico.")
    parser.add_argument("--firmware", required=True, help="Path to the firmware .elf file.")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port of the Pico.")
    args = parser.parse_args()

    if not flash_firmware(args.firmware):
        sys.exit(1)

    # Give the device a moment to reset and start up
    time.sleep(2)

    if not run_tests(args.port):
        sys.exit(1)

if __name__ == "__main__":
    main()
