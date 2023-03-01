#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "arm_control.h"
#include "pwm_funcs.h"
#include "uart.h"

void arm_setup(uint8_t type)
{
    arm_state == RETRACTED;
    gripper_state == RETRACTED;
    arm_angle1 = 0;
    arm_angle2 = 0;
    gripper_angle = 0;
    check = 0;

    RC1 = 0;
    RC2 = 0;
    RC1PPS = 0x00;  // C1 source is Latch C1
    RC2PPS = 0x00;  // C2 source is Latch C2
    TRISC1 = 0;     // C1 is set to output
    TRISC2 = 0;     // C2 is set to output

    setup_timer();

    if (type == ARM)
    {
        setup_pwm(1);
        setup_pwm(2);
    }
    else if (type == GRIPPER)
    {
        setup_pwm(1);
    }
}

void arm_extend(void)
{
    if (arm_state == EXTENDED)
    {
        // uh oh
    }
    else if (arm_state == RETRACTED)
    {
        // go through a loop where the arm PWM is updated
        // to move it to the extended value
    }
}

void arm_retract(void)
{
    if (arm_state == EXTENDED)
    {
        // go through a loop where the arm PWM is updated
        // to move it to the extended value
        
    }
    else if (arm_state == RETRACTED)
    {
        // uh oh
    }
}

void gripper_open(void)
{

}

void gripper_close(void)
{

}

void send_error(uint8_t error_no)
{
    uint8_t return_data[4];
    return_data[0] = uart_get_address();
    return_data[1] = error_no;

    uart_send_frame(PI_ADDRESS, return_data, 2);
    reset_status();
}

void send_status(void)
{

}

void reset_status(void)
{
    check = 0;
    uart_reset();
}

void arm_receive_uart(void)
{

}