add_executable(pico_test
    test_main.c
    test_sample.c
)

# Add the Unity source file to the build
target_sources(pico_test PRIVATE
    ../unity/src/unity.c
)

# Add the Unity include directory
target_include_directories(pico_test PRIVATE
    ../unity/src
)

# Link to the Pico SDK and the CYW43 Wi-Fi/Bluetooth driver
target_link_libraries(pico_test
    pico_stdlib
    pico_cyw43_arch_none
)

# Enable USB and UART output
pico_enable_stdio_usb(pico_test 1)
pico_enable_stdio_uart(pico_test 1)

# Generate the .uf2 file for easy flashing
pico_add_extra_outputs(pico_test)
