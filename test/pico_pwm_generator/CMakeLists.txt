cmake_minimum_required(VERSION 3.13)

project(pico_pwm_generator C CXX ASM)

# Set information for picotool
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Add our source files
add_executable(pico_pwm_generator
    pico_pwm_generator.c
)

# Link to Pico SDK libraries
target_link_libraries(pico_pwm_generator pico_stdlib hardware_pwm)

# Enable USB output
pico_enable_stdio_usb(pico_pwm_generator 1)
pico_enable_stdio_uart(pico_pwm_generator 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(pico_pwm_generator)
