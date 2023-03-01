/* 
 * File:   arm_control.h
 * Author: andre
 *
 * Created on February 10, 2023, 6:10 PM
 */

#ifndef ARM_CONTROL_H
#define	ARM_CONTROL_H

// Types
#define ARM     1
#define GRIPPER 2

// States
#define RETRACTED 1
#define EXTENDED 2

// PWM values for arms
#define ARM1_EXTENDED 10
#define ARM1_RETRACTED 0
#define ARM2_EXTENDED 10
#define ARM2_RETRACTED 0
#define GRIPPER_EXTENDED 10
#define GRIPPER_RETRACTED 0


uint8_t arm_state, gripper_state,
        arm_angle1, arm_angle2, gripper_angle,
        check;


void arm_setup(uint8_t type);
void arm_extend(void);
void arm_retract(void);
void gripper_open(void);
void gripper_close(void);

void send_error(uint8_t error_no);
void send_status(void);
void reset_status(void);
void arm_receive_uart(void);



#endif	/* ARM_CONTROL_H */

