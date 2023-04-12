#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "motor_control.h"
#include "pwm_funcs.h"
#include "uart.h"


/*
    AP = C4
    AN = C3
    BP = C2
    BN = C1

    Forward: C2 & C3
    Reverse: C4 & C1
    Brake: C3 & C1
    Coast: all open

*/


void motor_setup(void)
{
    
    RC1 = 0;
    RC2 = 0;
    RC1PPS = 0x00;  // C1 source is Latch C1
    RC2PPS = 0x00;  // C2 source is Latch C2
    TRISC1 = 0;     // C1 is set to output
    TRISC2 = 0;     // C2 is set to output
    motor_ground_cutoff();
    setup_timer();
    setup_pwm(1);
    setup_pwm(2);
    motor_coast();

    motor_comm_state = IDLE_STATE;
    motor_reset_status();
}

void motor_forward(uint8_t speed)
{
    // Might need to ramp up to final speed to get robot moving
    if (current_state == FORWARD)
    {
        set_pwm_duty_cycle(1, speed);
    }
    else
    {
        //motor_ground_cutoff();
        pwm_off(1);
        pwm_off(2);
        
        __delay_us(20);    // Delay to ensure all the transistors are off

        pwm_on(1, speed);
        current_state = FORWARD;
    }

    current_speed = speed;
}

void motor_reverse(uint8_t speed)
{
    if (current_state == REVERSE)
    {
        set_pwm_duty_cycle(2, speed);
    }
    else
    {
        //motor_ground_cutoff();
        pwm_off(1);
        pwm_off(2);

        __delay_us(20);    // Delay to ensure all the transistors are off

        pwm_on(2, speed);
        current_state = REVERSE;
    }
    
    current_speed = speed;
}

void motor_coast(void)
{
    pwm_off(1);
    pwm_off(2);
    //motor_ground_cutoff();
    current_state = COAST;
    current_speed = 1;
    // Setting speed to 1, because the UART doesn't seem to like 0s
}

void motor_brake(uint8_t speed)
{
    // Might need to change this to just reversing the motors
    
    
    
        pwm_off(1);
        pwm_off(2);

        __delay_us(20);    // Delay to ensure all the transistors are off

        //pwm_on(1, speed);
        //pwm_on(2, speed);
        RC1 = 1;    // Set both sides high
        RC2 = 1;
        current_state = BRAKE;
        current_speed = 0;
    
    current_speed = speed;

    // Need to find out if brake force goes up with more voltage
}

void motor_ground_cutoff(void)
{
    RC1 = 0;
    RC3 = 0;
}

    /*
    * 4 fields for return_data:
    * 1. this address
    * 2. check value
    * 3. current direction
    * 4. current speed
    */
void motor_send_error(uint8_t error_no)
{
    // Need to set up error types
    uint8_t return_data[4];
    return_data[0] = uart_get_address();
    return_data[1] = error_no;

    uart_send_frame(PI_ADDRESS, return_data, 2);
    motor_reset_status();
}

void motor_send_status(void)
{
    uint8_t return_data[4];

    return_data[0] = uart_get_address();
    return_data[1] = check;
    return_data[2] = current_state;
    return_data[3] = current_speed;

    uart_send_frame(PI_ADDRESS, return_data, 4);
    motor_reset_status();
}

void motor_reset_status(void)
{
    new_state = 150;
    new_speed = 150;
    check = 0;
    uart_reset();
}

uint8_t valid_data(void)
{
    return (((new_speed < 100) && (new_speed > 0)) & (check == (new_state ^ new_speed)));
}

void motor_receive_uart(void)
{
    uint8_t motor_message = uart_receive();

    switch (motor_comm_state)
    {
        case IDLE_STATE:
            switch (motor_message)
            {
                case UART_ADDRESS_GOOD:
                    motor_comm_state = RECEIVE_DATA_STATE;  // Good address, receive data
                    break;

                case UART_ADDRESS_BAD:                      // Not for this MCU
                    break;
                
                default:
                    break;
            }
            break;
        case RECEIVE_DATA_STATE:
            switch (motor_message)
            {
                case UART_ADDRESS_GOOD:
                case UART_ADDRESS_BAD:
                case UART_END_OF_FRAME:
                case UART_IGNORE:
                case COMM_ERROR:
                    // None of these messages should be received here
                    motor_comm_state = IDLE_STATE;          // Reset to idle
                    motor_reset_status();                         // Reset all variables
                    motor_send_error(MISSING_DATA);               // Request new data
                    break;
                
                default:
                    if (new_state == 150)
                    {
                        new_state = motor_message;
                    }
                    else if (new_speed == 150)
                    {
                        new_speed = motor_message;
                    }
                    else
                    {
                        check = motor_message;
                        motor_comm_state = EOF_STATE;
                    }
                    break;
            }
            break;

        case EOF_STATE:
                if (motor_message == UART_END_OF_FRAME)
                {
                    motor_comm_state = IDLE_STATE;          // No matter what, go back to idle
                    switch (new_state)
                    {
                        case FORWARD:
                            if (valid_data())
                            {
                                motor_forward(new_speed);
                                motor_send_status();
                            }
                            else
                            {
                                motor_send_error(BAD_DATA);
                            }
                            break;
                        
                        case REVERSE:
                            if (valid_data())
                            {
                                motor_reverse(new_speed);
                                motor_send_status();
                            }
                            else
                            {
                                motor_send_error(BAD_DATA);
                            }
                            break;

                        case COAST:
                            if (valid_data())
                            {
                                motor_coast();
                                motor_send_status();
                            }
                            else
                            {
                                motor_send_error(BAD_DATA);
                            }
                            break;

                        case BRAKE:
                            if (valid_data())
                            {
                                motor_brake(new_speed);
                                motor_send_status();
                            }
                            else
                            {
                                motor_send_error(BAD_DATA);
                            }
                        
                        case MOTOR_STATUS:
                            motor_send_status();
                            break;
                    
                        default:
                            motor_reset_status();
                            motor_send_error(BAD_DATA);
                            break;
                    }
                }
                else
                {
                    motor_comm_state = IDLE_STATE;
                    motor_reset_status();
                    motor_send_error(MISSING_EOF);
                }
                break;
        
        default:
            uart_reset();
            break;
    }
}

void motor_receive_uart_frame(void)
{
    if (frame_index == FRAME_MOTOR)
    {
        new_state = frame[0];
        new_speed = frame[1];
        check = frame[2];
        if (valid_data())
        {
            switch (new_state)
            {
                case FORWARD:
                    if (valid_data())
                    {
                        motor_forward(new_speed);
                        motor_send_status();
                    }
                    else
                    {
                        motor_send_error(BAD_DATA);
                    }
                    break;
                
                case REVERSE:
                    if (valid_data())
                    {
                        motor_reverse(new_speed);
                        motor_send_status();
                    }
                    else
                    {
                        motor_send_error(BAD_DATA);
                    }
                    break;

                case COAST:
                    if (valid_data())
                    {
                        motor_coast();
                        motor_send_status();
                    }
                    else
                    {
                        motor_send_error(BAD_DATA);
                    }
                    break;

                case BRAKE:
                    if (valid_data())
                    {
                        motor_brake(new_speed);
                        motor_send_status();
                    }
                    else
                    {
                        motor_send_error(BAD_DATA);
                    }
                
                case MOTOR_STATUS:
                    motor_send_status();
                    break;
            
                default:
                    motor_reset_status();
                    motor_send_error(BAD_DATA);
                    break;
            }
        }
    }
    else
    {
        motor_send_error(BAD_DATA);
    }
}