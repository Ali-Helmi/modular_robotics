/* 
 * File:   arm_control.h
 * Author: andre
 *
 * Created on February 10, 2023, 6:10 PM
 */

#ifndef ARM_CONTROL_H
#define	ARM_CONTROL_H

// Types

// States
#define ARM_RETRACTED 1
#define ARM_EXTENDED 2
#define ARM_STATUS 3

// PWM values for arms
#define ARM1_EXTENDED 50
#define ARM1_RETRACTED 0
#define ARM2_EXTENDED 50
#define ARM2_RETRACTED 0
#define GRIPPER_EXTENDED 50
#define GRIPPER_RETRACTED 0

#define ARM_STEPS 5
#define GRIPPER_STEPS 5

// UART States
#define IDLE_STATE            1
#define RECEIVE_DATA_STATE    2
#define EOF_STATE             3


uint8_t arm_state, new_arm_state,
        arm1_current_value, arm2_current_value,
        arm1_desired_value, arm2_desired_value,
        check;

uint8_t arm_comm_state, new_state, arm_type, arm_error;

void arm_setup(void);
void arm_extend(void);
void arm_retract(void);
void gripper_open(void);
void gripper_close(void);

void arm_send_error(uint8_t error_no);
void arm_send_status(void);
void arm_reset_status(void);
void arm_receive_uart(void);

void arm_receive_uart_frame(void);



#endif	/* ARM_CONTROL_H */

