#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define _XTAL_FREQ 32000000

#include "uart.h"

/*
    SP1BRG baud rate generator = 25

    Page 231 for baud rate generator values

*/

void setup_uart(uint8_t address)
{
    mcu_address = address;
    uart_state = UART_IDLE;

    frame_index = 0;

    RC1IE = 1;  // Enable UART recieve interrupt

    // 115200 baud rate
    SP1BRG = 68;    // Set baud rate generator for 115200
    SYNC = 0;       // Asynchronous
    SPEN = 1;       // Serial port enable
    BRGH = 1;       // Set high baud rate
    BRG16 = 1;      // 16 bit baud rate generator

    // Transmit
    TRISA5 = 1;
    RA5PPS = 0x00;
    //RA5PPS = 0x05;  // Transmit pin
    TX9 = 0;        // 8 bit transmission
    SCKP = 0;       // Set clock polarity
    TXEN = 1;       // Enable transmission

    // Receive
    RX1PPSbits.PORT = 0;                // Receive on port A
    RX1PPSbits.PIN = 4;                 // Receive on pin 4
    ANSELA = ANSELA & ~(0b00010000);    // Clear ansel for A4
    RX9 = 0;                            // Disable receiving 9 bits
    ADDEN = 0;                          // Enable Address 
    CREN = 1;                           // Enable continuous receive
}

uint8_t uart_receive(void)
{
    uint8_t uart_message, recv_address;
    
    uart_message = RC1REG;

    frame[frame_index++] = uart_message;

    if ((FERR == 0) & (OERR == 0))  // No frame error or overrun
    {
        // UART state machine
        switch (uart_state)
        {
            case UART_IDLE:
                if (((uart_message & 128) >> 7) == 1)    // Check if this is an address byte
                {
                    recv_address = uart_message & 127;   // remove msb to get address
                    if (mcu_address == recv_address)
                    {
                        uart_state = UART_MESSAGE;  // Move on to receive message state
                        return UART_ADDRESS_GOOD;   // Tell the caller to expect data
                    }
                    else
                    {
                        return UART_IGNORE;        // Tell the caller to ignore
                    }
                }
                else
                {
                    return UART_IGNORE;             // Tell the caller to ignore
                }
                break;

            case UART_MESSAGE:
                if (uart_message == END_TOKEN)           // Check for an end token
                {
                    uart_state = UART_IDLE;         // Return to idle state
                    return UART_END_OF_FRAME;       // Tell the caller the frame has ended
                }
                else if (((uart_message & 128) >> 7) == 1)   // Check for an address byte
                {
                    uart_state = UART_IDLE;         // Go back to idle
                    return UART_FRAME_ERROR;        // Tell the caller there is a frame error
                }
                else
                {
                    return uart_message;                 // Return the message
                }
                break;
        
            default:
                uart_state = UART_IDLE;
                return COMM_ERROR;
                break;
        }        
    }
    else
    {
        /*
        if (OERR)
        {
            uint8_t msg;
            msg = RC1REG;
            msg = RC1REG;
            CREN = 0;
            CREN = 1;
        }
        */
        return COMM_ERROR;                       // Frame error or overrun, message not good
    }
}

// Need to have transmit disabled until ready to send
void uart_send_byte(uint8_t data)
{
    TX1REG = data;   // Send data byte
}


void uart_send_frame(uint8_t address, const uint8_t * data, uint8_t length)
{
    GIE = 0;                    // Disable interrupts
    while(!TRMT) {  }           // Wait for the transmit register to empty
    RA5PPS = 0x05;              // Set port A5 to be TX
    TX1REG = 128 + address;     // Transmit the address
    while (length)
    {
        while(!TRMT) {  }       // Wait for the transmit register to empty
        TX1REG = *(data++);     // Transmit the next byte
        length--;
    }
    while(!TRMT) {  }           // Wait for the transmit register to empty
    TX1REG = END_TOKEN;         // Send the frame end token
    while(!TRMT) {  }           // Wait for the transmit register to empty
    RA5PPS = 0x00;              // Set port A5 back to high impedance
    GIE = 1;                    // Enable interrupts
}

uint8_t uart_get_address(void)
{
    return mcu_address;
}

void uart_reset(void)
{
    uart_state = UART_IDLE;
    //addr_good = 0;
    //eof_received = 1;
    // clear out receive FIFO
    uint8_t msg;
    msg = RC1REG;
    msg = RC1REG;
    CREN = 0;
    CREN = 1;
    
    frame_index = 0;
}

uint8_t uart_receive_frame(void)
{
    uint8_t uart_message = RC1REG;
    uint8_t recv_address;

    if ((FERR == 0) & (OERR == 0))
    {
        switch (uart_state)
        {
            case UART_IDLE:
                if (((uart_message & 128) >> 7) == 1)    // Check if this is an address byte
                {
                    recv_address = uart_message & 127;   // remove msb to get address
                    if (mcu_address == recv_address)
                    {
                        uart_state = UART_MESSAGE;  // Move on to receive message state
                        frame_index = 0;            // Set the frame index to the start of the array
                    }
                }
                break;

            case UART_MESSAGE:
                if (uart_message == END_TOKEN)           
                {
                    // Check for an end token
                    uart_state = UART_IDLE;             // Return to idle state
                    return 1;                           // EOF received
                    
                }
                else if (((uart_message & 128) >> 7) == 1)   
                {
                    // Check for an address byte
                    uart_state = UART_IDLE;         // Go back to idle
                    frame_index = 0;                // Reset frame index
                    return MISSING_EOF;             // Never saw an EOF byte
                }
                else if (frame_index > 5)
                {
                    // Received too many message bytes, something is wrong
                    uart_state = UART_IDLE;
                    frame_index = 0;
                    return MISSING_EOF;
                }
                else
                {
                    frame[frame_index++] = uart_message;
                }
                break;
        
            default:
                uart_state = UART_IDLE;
                return COMM_ERROR;
                break;
        }
    }
    return 0;       // Frame is either still building, or not for this module
}