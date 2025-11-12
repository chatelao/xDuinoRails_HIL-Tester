#include "pico/stdlib.h"
#include "hardware/pwm.h"

// Define the GPIO pin for PWM output
#define PWM_PIN 16

int main() {
    // Set up the PWM pin
    gpio_set_function(PWM_PIN, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(PWM_PIN);

    // Set the PWM frequency
    pwm_config config = pwm_get_default_config();
    // Set the clock divider to run the PWM at 1 MHz
    pwm_config_set_clkdiv(&config, 125.0f);
    // Set the wrap value to 1000, so the PWM frequency is 1 kHz
    pwm_config_set_wrap(&config, 1000);
    pwm_init(slice_num, &config, true);

    // Set the PWM duty cycle to 50%
    pwm_set_gpio_level(PWM_PIN, 500);

    // The PWM is now running in the background.
    // The main loop can be empty.
    while (1) {
        tight_loop_contents();
    }
}
