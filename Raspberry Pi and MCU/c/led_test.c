#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "uart.h"
#include "led_test.h"

void toggle_LED(void)
{
    RC0 = ~RC0;
}

void led_receive_uart(void)
{
    message = uart_receive();

    if (message == ADDRESS_GOOD)
    {
        receive = 1;
    }
    else if (message == ADDRESS_BAD)
    {
        // Do nothing
    }
    else if (message == END_OF_FRAME)
    {
        receive = 0;
        uint8_t data[1];
        data[0] = 1;

        uart_send_frame(PI_ADDRESS, data, 1);
    }
    else
    {
        toggle_LED();
    }
    
}