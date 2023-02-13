/* 
 * File:   uart.h
 * Author: andre
 *
 * Created on October 16, 2022, 5:38 PM
 */

#ifndef UART_H
#define	UART_H


#define _XTAL_FREQ 32000000
#define PI_ADDRESS 33

// UART states
#define UART_IDLE       1
#define UART_MESSAGE    2


// Message returns
#define UART_ADDRESS_GOOD   200
#define UART_ADDRESS_BAD    201
#define UART_END_OF_FRAME   202
#define UART_ERROR          203
#define UART_FRAME_ERROR    204
#define UART_IGNORE         204

#define END_TOKEN       126

uint8_t uart_state, mcu_address, addr_good = 0, eof_received = 1;

uint8_t frame_index;
uint8_t frame[5];


void setup_uart(uint8_t address);
uint8_t uart_receive(void);
void uart_send_byte(uint8_t data);
void uart_send_frame(uint8_t address, const uint8_t * data, uint8_t length);
uint8_t uart_get_address(void);
void uart_reset(void);


#endif	/* UART_H */