
:::::::WIN7/8/10 OS::::

1¡¢Unzip file  XiaoRGEEK_raspberrypi_8G_20170627.gz £¨It is recommended to use the latest version of the firmware£©
   Unzip file 'XiaoRGEEK_raspberrypi_8G_20170627.gz'
   
2¡¢Formatting the SD card with the SDFormatter tool
	Use the SDFormatter tool to format the SD card
	
3¡¢Use Win32DiskImager-0.9.5-binary£¬Select the.Img file unpacked in step 1£¬and write¡£
	Using Win32DiskImager-0.9.5-binary, select the.Img file extracted in step 1, and write
	
4¡¢DONE

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
Version Description:
	20170927:
			1¡¢SSID added the WLAN0 MAC address as a suffix to facilitate the simultaneous use of multiple raspberry pi cars
				ssid£ºwifi-robots.com_(12 digit MAC address)
				password£º12345678
			
	20170722:
			1¡¢New add motor speed control function
			2¡¢New add sensor multi-function mode
	
	20170627:
			1¡¢New add support PWR.A53.B motherboard
			2¡¢Built-in python OPENCV£¨python2.7£©
			3¡¢Built-in SMBUS include XRservo function£º
				a¡¢Set the angle of the servo   XRservo.XiaoRGEEK_SetServo(0x01,angle)
					This function is to set the No.1 servo angle is angle.		
				b¡¢Memory of the servo angle, storage of all current servo angle values.
					XRservo.XiaoRGEEK_SaveServo()
				c¡¢Restore all the servo to the stored angle
					XRservo.XiaoRGEEK_ReSetServo()
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::