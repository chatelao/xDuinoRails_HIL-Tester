cmake_minimum_required(VERSION 3.13)

# Set the board to Raspberry Pi Pico W BEFORE including the SDK
# This ensures all subsequent includes and initializations use the correct board
set(PICO_BOARD pico_w)

# Set the C standard to C11
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Set the path to the Pico SDK
set(PICO_SDK_PATH "${CMAKE_CURRENT_SOURCE_DIR}/pico-sdk")

# Include the Pico SDK
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hil_tester C CXX ASM)

# Initialize the Pico SDK
pico_sdk_init()

# Add the test directory
add_subdirectory(test)
