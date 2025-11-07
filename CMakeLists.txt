cmake_minimum_required(VERSION 3.13)

# Set the C standard to C11
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Set the path to the Pico SDK
# This will likely need to be adjusted on the runner
set(PICO_SDK_PATH "../../pico-sdk")

# Include the Pico SDK
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hil_tester C CXX ASM)

# Add the test directory
add_subdirectory(test)
