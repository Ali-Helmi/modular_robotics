#include <xc.h>
#include <pic16f15224.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define _XTAL_FREQ 32000000

#include "pwm_funcs.h"

uint8_t ch1_duty = 0;
uint8_t ch2_duty = 0;

void setup_timer(void)
{
    // Timer2 setup
    T2PR = 0xFA;                // Load T2PR register with period of 250
    //T2PR = 0x9B;                 // Load T2PR register with 155
    TMR2IF = 0;                 // Clear TMR2IF flag
    T2CLKCON = 0b00000001;      // Set clock source to Fosc/4
    //T2CLKCON = 0b00000101;      // Set clock source to MFINTOSC
    T2CONbits.CKPS = 0b110;     // 1:64 prescaler
    //T2CONbits.CKPS = 0b110;     // 1:16 prescaler
    T2CONbits.OUTPS = 0b0000;   // 1:1 postscaler
    //T2CONbits.OUTPS = 0b1001;   // 1:10 postscaler
    T2CONbits.ON = 1;           // Timer on
    

    while(TMR2IF != 1) {}         // Wait until TMR2IF is set
}

void setup_pwm(uint8_t channel)
{
    // page 215 setup PWM
    // PWM set up
    if (channel == 1)
    {
        TRISC2 = 1;         // Set Port C2 to tristate
        RC2PPS = 0x03;      // Set PortC2 to be PWM3
        PWM3CON = 0x00;     // Clear the PWM3CON register
    }
    else if (channel == 2)
    {
        TRISC1 = 1;         // Set Port C1 to tristate
        RC1PPS = 0x04;      // Set PortC1 to be PWM4
        PWM4CON = 0x00;     // Clear the PWM4CON register
    }
    
    set_pwm_duty_cycle(channel, 0);     // Set PWM duty cycle to 0, or high
    
    if (channel == 1)
    {
        TRISC2 = 0;     // C2 is set to output
        PWM3EN = 1;     // PWM2 enable
        PWM3OUT = 1;    // PM3 Output
        PWM3POL = 1;    // PM3 polarity normal
    }
    else if (channel == 2)
    {
        TRISC1 = 0;     // C1 is set to output
        PWM4EN = 1;     // PWM4 enabled
        PWM4OUT = 1;    // PWM4 output
        PWM4POL = 1;    // PWM4 polarity normal
    }
    
}

void set_pwm_duty_cycle(uint8_t channel, uint32_t percent)
{
    uint32_t duty_cycle = 1024 - (percent * 1024 / 100);    // Get inverse percentage of 1024
    //uint32_t duty_cycle = 512 - (percent * 512 / 100);    // Get inverse percentage of 512
    
    if (channel == 1)
    {
        PWM3DC = (uint16_t) duty_cycle  << 6;   // Shift left 6 bits to set PWM3DC
    } else if (channel == 2) 
    {
        PWM4DC = (uint16_t) duty_cycle  << 6;   // Shift left 6 bits to set PWM4DC
    }
}

void set_pwm_raw_duty_cycle(uint8_t channel, uint16_t duty_cycle)
{
    //uint32_t duty_cycle = 1024 - (percent * 1024 / 100);    // Get inverse percentage of 1024
    //uint32_t duty_cycle = 512 - (percent * 512 / 100);    // Get inverse percentage of 512
    
    if (channel == 1)
    {
        PWM3DC = (uint16_t) duty_cycle  << 6;   // Shift left 6 bits to set PWM3DC
    } else if (channel == 2) 
    {
        PWM4DC = (uint16_t) duty_cycle  << 6;   // Shift left 6 bits to set PWM4DC
    }
}

/*
    pmos need inverse PWM, nmos will just be digital signals.
    Need to make sure there is a 1ms delay between turning any transistor off
    and turning any others on to prevent short circuit.

*/

void pwm_on(uint8_t channel, uint8_t duty_cycle)
{
    if (channel == 1)
    {
        set_pwm_duty_cycle(channel, duty_cycle);
        RC2PPS = 0x03;      // Set PortC2 to be PWM3
    } else if (channel == 2)
    {
        set_pwm_duty_cycle(channel, duty_cycle);
        RC1PPS = 0x04;      // Set PortC1 to be PWM4
    }
    
}

void pwm_off(uint8_t channel)
{
    if (channel == 1)
    {
        RC2 = 0;            // Set output low
        RC2PPS = 0x00;      // Set C2 to be digital ouput
    } else if (channel == 2) {
        RC1 = 0;            // Set output low
        RC1PPS = 0x00;      // Set C4 to be digital output
        
    }
}

