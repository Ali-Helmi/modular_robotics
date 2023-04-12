/* 
 * File:   sensor.h
 * Author: andre
 *
 * Created on November 8, 2022, 11:26 AM
 */

#ifndef SENSOR_H
#define	SENSOR_H



// Sensor UART states
#define READ_SENSOR 5
#define SEND_DATA   7

// Sensor states
#define IDLE 0
#define TRIGGER 1
#define READ_WAIT 2
#define READING 3

// UART States
#define IDLE_STATE            1
#define RECEIVE_DATA_STATE    2
#define EOF_STATE             3

#define SENSOR_READ     1
#define SENSOR_SEND     2

uint8_t sensor_comm_state, message, state, check, request_type;
uint16_t microseconds, distance, wait_timeout;

void sensor_setup(void);

void sensor_send_error(uint8_t error_no);
void sensor_send_status(void);
void sensor_reset_status(void);
void sensor_receive_uart(void);

void sensor_receive_uart_frame();

void sensor_pulse(void);
void sensor_read(void);

void sensor_timer_reset(void);


#endif	/* SENSOR_H */

