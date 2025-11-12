cmake_minimum_required(VERSION 3.13)

set(PICO_BOARD pico_w)

add_executable(blinky
    main.c
)

# Enable USB UART output
pico_enable_stdio_usb(blinky 1)
pico_enable_stdio_uart(blinky 0)

# Link to Pico libraries
target_link_libraries(blinky pico_stdlib pico_cyw43_arch_none)

# Add the include directory for the cyw43 driver
target_include_directories(blinky PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../../pico-sdk/src/rp2_common/pico_cyw43_arch/include
)

# create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(blinky)
