# -*- coding: utf-8 -*- 
from datetime import datetime as dt
import time
import locale
import os
import RPi.GPIO as GPIO

class weight:
	GPIO.setmode(GPIO.BCM)

	# データ格納
	date = ""
	value = ""

	def readadc(adcnum, clockpin, mosipin, misopin, cspin):
		if ((adcnum > 7) or (adcnum < 0)):
			return -1
		GPIO.output(cspin, True)

		GPIO.output(clockpin, False)  # start clock low
		GPIO.output(cspin, False)     # bring CS low

		commandout = adcnum
		commandout |= 0x18  # start bit + single-ended bit
		commandout <<= 3    # we only need to send 5 bits here
		for i in range(5):
			if (commandout & 0x80):
				GPIO.output(mosipin, True)
			else:
				GPIO.output(mosipin, False)
			commandout <<= 1
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)

		adcout = 0
		# read in one empty bit, one null bit and 10 ADC bits
		for i in range(12):
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)
			adcout <<= 1
			if (GPIO.input(misopin)):
				adcout |= 0x1

		GPIO.output(cspin, True)

		adcout >>= 1       # first bit is 'null' so drop it
		return adcout

	def median(ls):
		return sorted(ls)[len(ls)//2]

	# change these as desired - they're the pins connected from the
	# SPI port on the ADC to the Cobbler
	SPICLK = 18
	SPIMISO = 23
	SPIMOSI = 24
	SPICS = 25

	def measure(self):
		# set up the SPI interface pins
		GPIO.setup(SPIMOSI, GPIO.OUT)
		GPIO.setup(SPIMISO, GPIO.IN)
		GPIO.setup(SPICLK, GPIO.OUT)
		GPIO.setup(SPICS, GPIO.OUT)

		# 10k trim pot connected to adc #0
		potentiometer_adc = 0;

		last_read = 0       # this keeps track of the last potentiometer value
		tolerance = 5       # to keep from being jittery we'll only change
				    # volume when the pot has moved more than 5 'counts'

		count = 0
		count_max = 20
		while count < count_max:
			# we'll assume that the pot didn't move
			trim_pot_changed = False

			# read the analog pin
			trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

			# 抵抗10k
			R1 = 10.0
			# アナログ入力値から出力電圧を計算
			Vo = trim_pot * 5.0 / 1024
			# 出力電圧からFRSの抵抗値を計算
			Rf = R1*Vo / (5.0 - Vo)
			# FRSの抵抗値から圧力センサの荷重を計算
			fg = 880.79/Rf + 47.96

			tdatetime = dt.now()
			self.date = tdatetime.strftime('%Y/%m/%d %H:00:00')
			self.value = fg

			# hang out and do nothing for a half second
			time.sleep(0.1)

			count += 1
		else:
			GPIO.cleanup()
