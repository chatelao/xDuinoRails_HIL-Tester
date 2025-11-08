#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "pico/stdio.h"
#include <stdio.h>

int main() {
    stdio_init_all();

    if (cyw43_arch_init()) {
        printf("Wi-Fi init failed");
        return -1;
    }

    for (int i = 0; i < 20; i++) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(100);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(100);
        printf("LED toggled\n");
    }

    return 0;
}
