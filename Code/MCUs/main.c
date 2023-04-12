/* 
 * File:   main.c
 * Author: andre
 *
 * Created on October 10, 2022, 10:32 PM
 */

// PIC16F15224 Configuration Bit Settings
// 'C' source line config statements
// CONFIG1
#pragma config FEXTOSC = OFF    // External Oscillator Mode Selection bits (Oscillator not enabled)
#pragma config RSTOSC = HFINTOSC_32MHZ// Power-up Default Value for COSC bits (HFINTOSC (32 MHz))
#pragma config CLKOUTEN = OFF   // Clock Out Enable bit (CLKOUT function is disabled; I/O function on RA4)
#pragma config VDDAR = HI       // VDD Range Analog Calibration Selection bit (Internal analog systems are calibrated for operation between VDD = 2.3V - 5.5V)

// CONFIG2
#pragma config MCLRE = EXTMCLR  // Master Clear Enable bit (If LVP = 0, MCLR pin is MCLR; If LVP = 1, RA3 pin function is MCLR)
#pragma config PWRTS = PWRT_16  // Power-up Timer Selection bits (PWRT set at 16 ms)
#pragma config WDTE = OFF    // WDT Operating Mode bits (WDT disabled; SEN is ignored)
#pragma config BOREN = ON       // Brown-out Reset Enable bits (Brown-out Reset Enabled, SBOREN bit is ignored)
#pragma config BORV = LO        // Brown-out Reset Voltage Selection bit (Brown-out Reset Voltage (VBOR) set to 1.9V)
#pragma config PPS1WAY = ON     // PPSLOCKED One-Way Set Enable bit (The PPSLOCKED bit can be set once after an unlocking sequence is executed; once PPSLOCKED is set, all future changes to PPS registers are prevented)
#pragma config STVREN = ON      // Stack Overflow/Underflow Reset Enable bit (Stack Overflow or Underflow will cause a reset)

// CONFIG3

// CONFIG4
#pragma config BBSIZE = BB512   // Boot Block Size Selection bits (512 words boot block size)
#pragma config BBEN = OFF       // Boot Block Enable bit (Boot Block is disabled
#pragma config SAFEN = OFF      // SAF Enable bit (SAF is disabled)
#pragma config WRTAPP = OFF     // Application Block Write Protection bit (Application Block is not write-protected)
#pragma config WRTB = OFF       // Boot Block Write Protection bit (Boot Block is not write-protected)
#pragma config WRTC = OFF       // Configuration Registers Write Protection bit (Configuration Registers are not write-protected)
#pragma config WRTSAF = OFF     // Storage Area Flash (SAF) Write Protection bit (SAF is not write-protected)
#pragma config LVP = ON         // Low Voltage Programming Enable bit (Low Voltage programming enabled. MCLR/Vpp pin function is MCLR. MCLRE Configuration bit is ignored.)

// CONFIG5
#pragma config CP = OFF         // User Program Flash Memory Code Protection bit (User Program Flash Memory code protection is disabled)

// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

#include <xc.h>


#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "pwm_funcs.h"
#include "motor_control.h"
#include "uart.h"
#include "sensor.h"
#include "arm_control.h"
//#include "led_test.h"

#define _XTAL_FREQ 32000000

#define MOTOR 1
#define ARM 2
#define SENSOR 3
#define TEST 10

// Set module type and MCU address
uint8_t module_type = ARM;
#define MCU_ADDRESS 5

int main(int argc, char** argv) {
    // Interrupt setup
    PIE0 = 0x00;    // Disable all external interrupts
    PIE1 = 0x00;
    PIE2 = 0x00;
    //INTF = 0;
    GIE = 1;    // Enable global interrupts
    PEIE = 1;   // Enable peripheral interrupts
    INTEDG = 1; // Interrupts on rising edge

    // PortC setup
    PORTC = 0x00;   // Set port c to 0
    LATC = 0x00;    // Set latch c to 0
    ANSELC = 0x00;  // Disable analog for port c
    //INLVLC = 0x00;
    SLRCONC = 0x00;
    TRISC = 0x00;   // set all c outputs to 0

    if (module_type == MOTOR)
    {
        motor_setup();
    }
    else if (module_type == SENSOR)
    {
        sensor_setup();
    }
    else if (module_type == ARM_MAIN)
    {
        //motor_setup();
        //motor_forward(10);
        arm_setup();
    }
    else if (module_type == TEST)
    {
        
    }
    

    setup_uart(MCU_ADDRESS); // set up UART with address

    uint16_t arm_pwm = 10;
    uint8_t up = 1;
    uint16_t delay_time = 200;
    
    while(1)
    {

        __delay_ms(25);

        if (module_type == MOTOR)
        {
            //motor_forward(30);
        }
        else if (module_type == SENSOR)
        {
            //sensor_pulse();
        }
        else if (module_type == ARM)
        {
            // Check if new PWM values have been requested
            // If so, change them.
            if (arm1_desired_value != arm1_current_value)
            {
                //arm1_current_value = arm1_desired_value;
                //set_pwm_duty_cycle(1, arm1_current_value);
                
                if (arm1_current_value < arm1_desired_value)
                {
                    set_pwm_duty_cycle(1, ++arm1_current_value);
                }
                else
                {
                    set_pwm_duty_cycle(1, --arm1_current_value);
                }
                
            }

            if (arm2_desired_value != arm2_current_value)
            {
                //arm2_current_value = arm2_desired_value;
                //set_pwm_duty_cycle(2, arm2_current_value);
                
                if (arm2_desired_value < arm2_current_value)
                {
                    set_pwm_duty_cycle(2, --arm2_current_value);
                }
                else
                {
                    set_pwm_duty_cycle(2, ++arm2_current_value);
                }
                
            }



        }
        //CLRWDT();
        
    }

    return (EXIT_SUCCESS);
}

// Interrupt code
void __interrupt() uart_int(void)
{
    // Need to disable interrupts besides RC1
    
    
    if (RC1IF == 1) // Check if interrupt is a UART receive
    {
        // Data is available in RC1REG
        // Read RC1REG to clear the flag

        // use generic uart receive frame
        if (uart_receive_frame() == 1)
        {
            // EOF received, call the function for this module type
            if (module_type == MOTOR)
            {
                motor_receive_uart_frame(); // change this to receive frame
            }
            else if (module_type == SENSOR)
            {
                sensor_receive_uart();
            }
            else if (module_type == ARM)
            {
                arm_receive_uart_frame();
            }
        }
        else
        {
            // if 0, no need to look into it
            // Other values might be errors
            
        }
    }
    else if (IOCCF1 == 1)     // External interrupt pin
    {
        IOCCF1 = 0; // Reset C2 interrupt
        if (module_type == SENSOR)
        {
            sensor_read();
        }
    }
    else
    {
        // check for int pin INTF
        // check for timer interrupt, increment microseconds
    }

    
}
