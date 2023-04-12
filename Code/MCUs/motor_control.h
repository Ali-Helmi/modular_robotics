/* 
 * File:   motor_control.h
 * Author: andre
 *
 * Created on October 21, 2022, 1:14 PM
 */

#ifndef MOTOR_CONTROL_H
#define	MOTOR_CONTROL_H

#define NMOS1 RC1    // C1
#define NMOS2 RC3    // C3

// States
#define FORWARD 1
#define REVERSE 2
#define COAST   3
#define BRAKE   4
#define MOTOR_STATUS    5

// UART States
#define IDLE_STATE            1
#define RECEIVE_DATA_STATE    2
#define EOF_STATE             3

#define MOTOR_FRAME_SIZE        3


uint8_t motor_comm_state, current_state, current_speed;
uint8_t new_state, new_speed, check;

void motor_setup(void);
void motor_forward(uint8_t speed);
void motor_reverse(uint8_t speed);
void motor_coast(void); // All transistors off
void motor_brake(uint8_t speed);
void motor_set_speed(uint8_t speed);

void motor_ground_cutoff(void);

void motor_send_error(uint8_t error_no);
void motor_send_status(void);
void motor_reset_status(void);
uint8_t check_data(void);
void motor_receive_uart(void);
void motor_receive_uart_frame(void);

#endif	/* MOTOR_CONTROL_H */

