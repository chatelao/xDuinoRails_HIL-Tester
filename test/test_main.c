#include "pico/stdlib.h"
#include "unity.h"
#include <stdio.h>

// Define the test runner function from the other test file
void run_test_suite(void);

void setUp(void) {
    // This function is called before each test
}

void tearDown(void) {
    // This function is called after each test
}

int main() {
    // Initialize stdio for UART output
    stdio_init_all();

    // A small delay to allow the serial port to initialize
    sleep_ms(2000);

    UNITY_BEGIN();

    // Run the test suite
    run_test_suite();

    UNITY_END();

    // Loop forever
    while (1);

    return 0;
}
