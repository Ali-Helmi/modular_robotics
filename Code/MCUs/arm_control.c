#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "arm_control.h"
#include "pwm_funcs.h"
#include "uart.h"

void arm_setup()
{
    arm_state = ARM_RETRACTED;
    check = 0;
    arm_comm_state = IDLE_STATE;
    new_state = 0;

    arm1_current_value = 50;
    arm2_current_value = 50;
    arm1_desired_value = 50;
    arm2_desired_value = 50;

    RC1 = 0;
    RC2 = 0;
    RC1PPS = 0x00;  // C1 source is Latch C1
    RC2PPS = 0x00;  // C2 source is Latch C2
    TRISC1 = 0;     // C1 is set to output
    TRISC2 = 0;     // C2 is set to output

    setup_timer();
    setup_pwm(1);
    setup_pwm(2);
    
    set_pwm_duty_cycle(1, arm1_current_value);
    set_pwm_duty_cycle(2, arm2_current_value);
}

void arm_extend(void)
{
    if (arm_state == ARM_EXTENDED)
    {
        // uh oh
    }
    else if (arm_state == ARM_RETRACTED)
    {
        // go through a loop where the arm PWM is updated
        // to move it to the extended value

        /*
        - Find current angle
        - construct a for loop that will take a certain number of steps
            towards the new angle
        */
        
        uint8_t number_of_steps = 5;
        for (uint8_t i = 1; i < 99; i++)
        {
            //arm_angle1 = 20 + (i * number_of_steps);
            set_pwm_duty_cycle(1, i);
            __delay_ms(25);
        }
        arm_state = ARM_EXTENDED;
    }
}

void arm_retract(void)
{
    if (arm_state == ARM_EXTENDED)
    {
        set_pwm_duty_cycle(1, 20);

        uint8_t number_of_steps = 5;
        for (uint8_t i = 99; i > 1; i--)
        {
            //arm_angle1 = 10 + (i * number_of_steps);
            set_pwm_duty_cycle(1, i);
            __delay_ms(25);
        }
        arm_state = ARM_RETRACTED;
        /*
        // go through a loop where the arm PWM is updated
        // to move it to the extended value
        if (arm_angle1 == ARM1_EXTENDED)
        {
            // Do full range of motion
            uint8_t number_of_steps = 10;
            for (uint8_t i = number_of_steps + 1; i > 0; i--)
            {
                arm_angle1 = i * ARM_STEPS;
                set_pwm_duty_cycle(1, arm_angle1);
                __delay_ms(30);
            }
            arm_state = ARM_RETRACTED;
        }
        */
        
    }
    else if (arm_state == ARM_RETRACTED)
    {
        // uh oh
    }
}

void arm_send_error(uint8_t error_no)
{
    uint8_t return_data[4];
    return_data[0] = uart_get_address();
    return_data[1] = error_no;

    uart_send_frame(PI_ADDRESS, return_data, 2);
    arm_reset_status();
}

void arm_send_status(void)
{
    uint8_t return_data[4];

    return_data[0] = uart_get_address();
    return_data[1] = arm1_desired_value;
    return_data[2] = arm2_desired_value;
    return_data[3] = check;

    uart_send_frame(PI_ADDRESS, return_data, 4);
    arm_reset_status();
}

void arm_reset_status(void)
{
    check = 0;
    uart_reset();
}

/*
void arm_receive_uart(void)
{
    uint8_t arm_message = uart_receive();
    arm_error = 0;

    switch (arm_comm_state)
    {
        case IDLE_STATE:
            switch(arm_message)
            {
                case UART_ADDRESS_GOOD:
                    arm_comm_state = RECEIVE_DATA_STATE;
                    break;
                
                case UART_ADDRESS_BAD:
                    break;
                
                default:
                    break;
            }
            break;

        case RECEIVE_DATA_STATE:
            switch (arm_message)
            {
                case UART_ADDRESS_GOOD:
                case UART_ADDRESS_BAD:
                case UART_END_OF_FRAME:
                case UART_IGNORE:
                case COMM_ERROR:
                    // None of these messages should be received here
                    arm_comm_state = IDLE_STATE;          // Reset to idle
                    arm_reset_status();                   // Reset all variables
                    arm_send_error(MISSING_DATA);         // Request new data
                    break;

                case ARM_EXTENDED:
                    new_arm_state = ARM_EXTENDED;
                    arm_comm_state = EOF_STATE;
                    break;

                case ARM_RETRACTED:
                    new_arm_state = ARM_RETRACTED;
                    arm_comm_state = EOF_STATE;
                    break;

                case ARM_STATUS:
                    new_arm_state = ARM_STATUS;
                    arm_comm_state = EOF_STATE;
                    break;

                default:
                    arm_comm_state = IDLE_STATE;          // Reset to idle
                    arm_reset_status();                   // Reset all variables
                    arm_send_error(MISSING_DATA);         // Request new data
                    break;
            }

        case EOF_STATE:
            if (arm_message == UART_END_OF_FRAME)
            {
                arm_comm_state = IDLE_STATE;
                arm_send_status();

                if (new_arm_state == ARM_EXTENDED)
                {
                    if (arm_type == ARM)
                    {
                        arm_extend();

                    }
                    else if (arm_type == GRIPPER)
                    {
                        gripper_open();
                    }
                }
                else if (new_arm_state == ARM_RETRACTED)
                {
                    if (arm_type == ARM)
                    {
                        arm_retract();
                    }
                    else if (arm_type == GRIPPER)
                    {
                        gripper_close();
                    }
                }

            }
            else
            {
                //arm_comm_state = IDLE_STATE;
                //arm_reset_status();
                //arm_send_error(MISSING_EOF);
            }
    }
}
*/


/*
    Arm frame:
    Byte    |   Name
    1       |   Arm 1 value
    2       |   Arm 2 value
    3       |   Check

    Values can be 1-99
    Value of 110 says to ignore that and leave the current

*/

void arm_receive_uart_frame()
{
    if (frame_index == FRAME_ARM)
    {
        uint8_t arm_message = frame[0];

        uint8_t arm1_request = frame[0],
                arm2_request = frame[1],
                values_validated = 0;
        
                
        check        = frame[2];

        if ((arm1_request ^ arm2_request) == check)
        {
            // Data is valid from the RPi

            if ((arm1_request > 0) & (arm1_request < 100))
            {
                // Arm1 data is in valid range
                values_validated += 1;
            }
            else if (arm1_request == 110)
            {
                // Not requesting to change the arm1 value
                values_validated += 4;
            }

            if ((arm2_request > 0) & (arm2_request < 100))
            {
                // Arm2 data is in valid range
                values_validated += 2;
            }
            else if (arm2_request == 111)
            {
                // Not requesting to change the arm2 value
                values_validated += 8;
            }

            switch (values_validated)
            {
                case 3:
                    // Update both arm values
                    arm1_desired_value = arm1_request;
                    arm2_desired_value = arm2_request;
                    arm_send_status();
                    break;

                case 9:
                    // Update only arm1
                    arm1_desired_value = arm1_request;
                    arm_send_status();
                    break;

                case 6:
                    // Update only arm2
                    arm2_desired_value = arm2_request;
                    arm_send_status();
                    break;

                case 12:
                    // Update nothing, just send status
                    arm_send_status();
                    break;


                default:
                    // Bad values were sent
                    arm_send_error(BAD_DATA);
                    break;
            }
        }
        else
        {
            // Bad check value
            arm_send_error(BAD_DATA);
        }

        
    }
    else
    {
        // Not neough data bytes
        arm_send_error(MISSING_DATA);
    }
}
        
/*
        switch (arm_message)
        {
            case ARM_EXTENDED:
                new_arm_state = ARM_EXTENDED;
                arm_send_status();
                arm_extend();\
                break;

            case ARM_RETRACTED:
                new_arm_state = ARM_RETRACTED;
                arm_send_status();
                arm_retract();
                break;

            case ARM_STATUS:
                arm_send_status();
                break;

            default:
                arm_reset_status();                   // Reset all variables
                arm_send_error(BAD_DATA);         // Request new data
                break;
        }
    }

    */



/*
 
 Gripper open: 45%
 Gripper close: 80%
 
 main arm idle
 * ch1 65
 * ch2 20
 * 
 main arm extended
 * ch1 tbd  poss: 25
 * ch2 tbd poss: 50
 
 * ch2 to 30 then change ch1
 * upper arm            lower arm
 
 * 
 * limitations
 * extended
 * ch1 25
  ch2 50
 * 
 * retracted
 * ch1 
 * ch2 
 */