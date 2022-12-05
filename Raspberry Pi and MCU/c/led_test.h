/* 
 * File:   led_test.h
 * Author: andre
 *
 * Created on November 6, 2022, 4:47 PM
 */

#ifndef LED_TEST_H
#define	LED_TEST_H

uint8_t message, receive = 0;


void toggle_LED(void);
void led_receive_uart(void);

#endif	/* LED_TEST_H */

