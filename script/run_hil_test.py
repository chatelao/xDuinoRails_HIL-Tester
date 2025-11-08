import serial
import subprocess
import time
import shutil

# --- Configuration ---
FIRMWARE_DIR = "build/test/sut/pico/blinky"
FIRMWARE_ELF = f"{FIRMWARE_DIR}/blinky.elf"
PICO_SERIAL_PORT = "/dev/ttyACM0"  # Adjust if your Pico uses a different port
BAUD_RATE = 115200
TIMEOUT = 10  # Seconds
EXPECTED_TOGGLES = 20

def build_firmware():
    """Builds the SUT firmware using CMake and Make."""
    print("--- Building SUT firmware ---")
    try:
        # Clean the build directory to ensure a fresh build
        if shutil.os.path.exists("build"):
            shutil.rmtree("build")

        subprocess.run(["cmake", "-B", "build", "-S", "."], check=True)
        subprocess.run(["make", "-C", "build"], check=True)
        print("--- Build successful ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building firmware: {e}")
        return False

def flash_firmware():
    """Flashes the firmware to the Pico using OpenOCD."""
    print("--- Flashing firmware ---")
    try:
        subprocess.run(
            [
                "openocd",
                "-f",
                "interface/raspberrypi-swd.cfg",
                "-f",
                "target/rp2040.cfg",
                "-c",
                f"program {FIRMWARE_ELF} verify reset exit",
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


def verify_blinking():
    """Verifies the blinking by listening for UART messages."""
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

def main():
    if not build_firmware():
        exit(1)
    if not flash_firmware():
        exit(1)
    if not verify_blinking():
        exit(1)

    print("--- HIL test completed successfully! ---")
    exit(0)

if __name__ == "__main__":
    main()
