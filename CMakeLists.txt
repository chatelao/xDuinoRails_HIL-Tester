cmake_minimum_required(VERSION 3.13)

# Set the C standard to C11
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Set the path to the Pico SDK
if (NOT PICO_SDK_PATH)
    if (DEFINED ENV{PICO_SDK_PATH})
        set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
    else()
        set(PICO_SDK_PATH "${CMAKE_CURRENT_SOURCE_DIR}/pico-sdk")
    endif()
endif()

# Include the Pico SDK
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hil_tester C CXX ASM)

# Set the board to Raspberry Pi Pico W for CYW43 wireless/LED driver support
set(PICO_BOARD pico_w)

# Initialize the Pico SDK
pico_sdk_init()

# Add the test directory
add_subdirectory(test)
