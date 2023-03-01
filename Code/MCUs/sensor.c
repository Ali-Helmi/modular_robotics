
#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "sensor.h"
#include "uart.h"

#define _XTAL_FREQ 32000000

// RPi sends message to read sensor, then will call later to get info back.
// Set up interrupt pin on receive to get data back

void sensor_setup(void)
{
    // setup INTPPS to be the receive pin
    // INTEDG 1
    // INTE 1
    // 
    TRISC1 = 1;             // Port C2 input

    IOCIE = 1;
    IOCCN1 = 1;
    IOCCP1 = 1;

    // set up timer
    T1CONbits.CKPS = 3;     // 1:8 prescaler
    T1CONbits.RD16 = 1;     // Read 16 bits
    T1CONbits.ON = 0;       // Have timer be off
    T1GCONbits.GE = 0;      // Always counting
    T1CLKbits.CS = 3;       // HFINTOSC

    TMR1H = 0;            // Preset
    TMR1L = 0;


    microseconds = 0;
    distance = 0;
    check = 0;

}

void sensor_timer_reset(void)
{
    TMR1IF = 0;     // Reset Timer 1 interrupt flag
    TMR1IE = 0;     // Reenable timer 1 interrupt
    TMR1H = 0;    // Set the timer 1 preset
    TMR1L = 0;
}

void sensor_pulse(void)
{
    // Hold pin high for 10us

    RC2 = 1;
    __delay_us(10);
    RC2 = 0;

    // set up interrupt for response on rising edge
    //INTE = 1;       // Enable interrupt pin
    //INTEDG = 1;     // Interrupt on rising edge
    state = READ_WAIT;
}

void sensor_read(void)
{
    // Call when pulse returned, triggered by rising edge
    // change interrupt to be falling edge
    // use capture to measure time between pulses

    // Send UART frame from here?
    // Could end up colliding with another MCU

    if (state == READ_WAIT)
    {
        //INTEDG = 0;     // Interrupt on falling edge to detect end of pulse
        microseconds = 0;   // Reset microsecond count
        sensor_timer_reset();
        T1CONbits.ON = 1;       // Have timer be on
        state = READING;
    }
    else if (state == READING)
    {
        T1CONbits.ON = 0;       // Turn timer off
        //INTE = 0;               // disable interrupt pin
        
        microseconds = (((uint16_t) TMR1H << 8) + TMR1L) / 4; 

        distance = (microseconds * 10) / 58;   // Distance in mm
        //distance = microseconds / 148; // Distance in inches

        state = IDLE;
    }
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
    uint8_t return_data[3];

    return_data[0] = uart_get_address();
    return_data[1] = check;

    if (request_type == SENSOR_READ)
    {
        return_data[2] = 1;
    }
    else if (request_type == SENSOR_SEND)
    {
        return_data[2] = distance;
    }
    else 
    {
        return_data[2] = 0;
    }

    uart_send_frame(PI_ADDRESS, return_data, 3);
    reset_status();
}

void reset_status(void)
{
    //check = 0;
    distance = 0;
    microseconds = 0;
    uart_reset();
}

void sensor_receive_uart(void)
{
    uint8_t sensor_message = uart_receive();

    switch (sensor_comm_state)
    {
        case IDLE_STATE:
            switch (sensor_message)
            {
                case UART_ADDRESS_GOOD:
                    sensor_comm_state = RECEIVE_DATA_STATE;  // Good address, receive data
                    break;

                case UART_ADDRESS_BAD:                      // Not for this MCU
                    break;
                
                default:
                    break;
            }
            break;
        case RECEIVE_DATA_STATE:
            switch (sensor_message)
            {
                case UART_ADDRESS_GOOD:
                case UART_ADDRESS_BAD:
                case UART_END_OF_FRAME:
                case UART_IGNORE:
                case UART_ERROR:
                    // None of these messages should be received here
                    sensor_comm_state = IDLE_STATE;          // Reset to idle
                    reset_status();                         // Reset all variables
                    send_error(MISSING_DATA);               // Request new data
                    break;
                
                default:
                    if (sensor_message ==  READ_SENSOR)
                    {
                        // RPi is saying to send a pulse
                        request_type = SENSOR_READ;
                    }
                    else if (sensor_message == SEND_DATA)
                    {
                        request_type = SENSOR_SEND;
                    }
                    else 
                    {
                        // Not read or send, so it is the check byte
                        check = message;
                        sensor_comm_state = EOF_STATE;
                    }
                    break;
            }
            break;

        case EOF_STATE:
                if (sensor_message == UART_END_OF_FRAME)
                {
                    sensor_comm_state = IDLE_STATE;          // No matter what, go back to idle
                    // Send the distance data to the pi

                    wait_timeout = 0;

                    while (state == READ_WAIT | state == READING)
                    {
                        // Possible endless loop here
                        // Put a check at the beginning of next UART frame
                        // to see if stuck here

                        if (wait_timeout++ > 7000)
                        {
                            // Haven't received a return pulse
                            // Object is more than 47 inches away
                            break;
                        }
                        __delay_us(1);
                    }
                    if (request_type == SENSOR_SEND)
                    {
                        // Send the pulse to measure distance
                        sensor_pulse();
                    }
                    send_status();
                }
                else
                {
                    sensor_comm_state = IDLE_STATE;
                    reset_status();
                    send_error(MISSING_EOF);
                }
                break;
        
        default:
            uart_reset();
            break;
    }


    //message = uart_receive();
/*
    if (message == ADDRESS_GOOD)
    {
        
    }
    else if (message == ADDRESS_BAD)
    {
        // Do nothing
    }
    else if (message == ERROR)
    {
        // An error has occurred, ask for a new message
        uint8_t data[1];
        data[0] = ERROR;

        uart_send_frame(PI_ADDRESS, data, 1);
    }
    else if (message == END_OF_FRAME)
    {
        uint8_t data[1];
        data[0] = distance & 0xff;
        uart_send_frame(PI_ADDRESS, data, 1);
    }
    else
    {
        // Unused for now
        if (message == READ_SENSOR)
        {

        }
        else if (message == SEND_DATA)
        {
            // distance data could be 3 bytes
            // 6 bits + 5 bits + 5 bits to get 16 bits
            // Plus a check byte
        }
    }
 */
}

