/*
*	RasPi Ultrasound
*	Created by: Andrew O'Shei
*/

#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <time.h>
#include <unistd.h>
#include <stdint.h>

#define TRIG 4
#define ECHO 5


void send_pulse();
void time_interrupt();

int flag = 2;
uint32_t start, stop, timeout;
float distance = 99.9;


int main(int argc, char *argv[])
{
	// Setup WiringPi
	if(wiringPiSetup() < 0)
	{
		printf("WiringPi setup failed!\n");
		exit(1);
	}

	printf("Initializing pins\n");
	pinMode(TRIG, OUTPUT);
	pinMode(ECHO, INPUT);
	pullUpDnControl(ECHO, PUD_DOWN);
	digitalWrite(TRIG, 0);
	delay(1000);

	// Setup the pin interrupt
	if(wiringPiISR(ECHO, INT_EDGE_BOTH, &time_interrupt) < 0)
	{
		printf("Failed to configure echo pin interrupt\n");
		exit(1);
	}

	while(1)
	{
		if(flag == 2)
		{
			if(distance < 10.0)
			{
				printf("Object detected!\n");
				exit(0);
			}
			flag = 0;
			timeout = 0;
			send_pulse();
		}
		if(flag == 1)
		{
			delay(10);
			if(++timeout > 50)
			{
				flag=2;
				//printf("Distance: Nan\n");
			}
		}
	}
	return 0;
}


void send_pulse()
{
	digitalWrite(TRIG, 0);
	delay(1);
	digitalWrite(TRIG, 1);
	delayMicroseconds(10);
	digitalWrite(TRIG, 0);
}

void time_interrupt()
{
	if(flag == 0)
	{
		start = micros();
		flag = 1;
	}
	else if (flag == 1)
	{
		stop = micros();
		distance = (float)(stop - start) / 58;
		//printf("Distance: %lf\n", distance);
		delay(100);
		flag = 2;
	}
}
