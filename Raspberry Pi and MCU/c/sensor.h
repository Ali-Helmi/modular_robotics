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

uint8_t message, state;
uint16_t microseconds, distance;

void sensor_setup(void);
void sensor_receive_uart(void);
void sensor_pulse(void);
void sensor_read(void);

void sensor_timer_reset(void);


#endif	/* SENSOR_H */

