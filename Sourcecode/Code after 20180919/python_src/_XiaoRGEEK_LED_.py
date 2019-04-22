#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_LED_.py
功    能：流水灯初始化以及大灯控制函数
外部条用：
from _XiaoRGEEK_LED_ import Robot_Led
XRLED = Robot_Led()
XRLED.FLOW_LED()	#流水灯函数
XRLED.Open_Light()	#开大灯
XRLED.Close_Light()	#关大灯
'''
import _XiaoRGEEK_GPIO_ as XR
import time


def	_FLOW_LED_():#流水灯
	print(" Flow led start...")
	XR.GPIOClr(XR.LED0)
	XR.GPIOClr(XR.LED1)
	XR.GPIOClr(XR.LED2)
	time.sleep(0.2)
	for i in range(0, 10):
		XR.GPIOSet(XR.LED0)
		XR.GPIOClr(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.2)
		XR.GPIOClr(XR.LED0)
		XR.GPIOSet(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.2)
		XR.GPIOClr(XR.LED0)
		XR.GPIOClr(XR.LED1)
		XR.GPIOSet(XR.LED2)
		time.sleep(0.2)
		XR.GPIOClr(XR.LED0)
		XR.GPIOClr(XR.LED1)
		XR.GPIOClr(XR.LED2)
		time.sleep(0.2)
	print(" Flow led over...")
####################################################
##函数名称 Open_Light()
##函数功能 开大灯LED0
##入口参数 ：无
##出口参数 ：无
####################################################
def	_Open_Light_():#开大灯LED0
	XR.GPIOClr(XR.LED0)#大灯正极接5V  负极接IO口
	time.sleep(0.5)

####################################################
##函数名称 Close_Light()
##函数功能 关大灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	_Close_Light_():#关大灯
	XR.GPIOSet(XR.LED0)#大灯正极接5V  负极接IO口
	time.sleep(0.5)

class Robot_Led:
	def __init__(self):
		pass
	def	Open_Light(self):
		_Open_Light_()
	def	Close_Light(self):
		_Close_Light_()
	def FLOW_LED(self):
		_FLOW_LED_()

