#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "unity.h"

// Test case to verify the onboard LED can be controlled
void test_led_initializes_and_toggles(void) {
    // Initialize the Wi-Fi chip/GPIO controller
    int init_result = cyw43_arch_init();
    TEST_ASSERT_EQUAL_INT(0, init_result);

    // Toggle the LED 5 times to confirm control
    for (int i = 0; i < 5; i++) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(50);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(50);
    }

    // De-initialize the Wi-Fi chip
    cyw43_arch_deinit();
}

// The test runner function that will be called from main
void run_test_suite(void) {
    RUN_TEST(test_led_initializes_and_toggles);
}
