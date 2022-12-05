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

#define FORWARD 1
#define REVERSE 2
#define COAST   3
#define BRAKE   4
#define MOTOR_STATUS    5
uint8_t current_state, current_speed;
uint8_t update, message, new_state, new_speed, check;

void motor_setup(void);
void motor_forward(uint8_t speed);
void motor_reverse(uint8_t speed);
void motor_coast(void); // All transistors off
void motor_brake(void); // PMOS on, NMOS off
void motor_set_speed(uint8_t speed);

void motor_ground_cutoff(void);

void motor_receive_uart(void);

#endif	/* MOTOR_CONTROL_H */

