#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
电机方向，由IN1 IN2 IN3 IN4来控制M1+/M1-;M2+/M2-输出
默认方向中：右侧电机接 M1+ M1-，且正向供电时，右侧是前进方向
			左侧电机接 M2+ M2-，且正向供电时，左侧是前进方向
如果接线有交叉，可以调换接线或者上位机中调整方向指令
'''
'''
文 件 名：_XiaoRGEEK_MOTOR_.py
功    能：电机方向控制函数
外部条用：
from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()

go.forward()		#上位机调整过方向后的前进
go.back()			#上位机调整过方向后的后退
go.left()			#上位机调整过方向后的左转
go.right()			#上位机调整过方向后的右转
go.stop()			#上位机调整过方向后的停止
go.M1_Speed(100)	#调整M1速度,0-100
go.M2_Speed(100)	#调整M2速度,0-100
'''

import _XiaoRGEEK_GPIO_ as XR
import _XiaoRGEEK_GLOBAL_variable_ as glo
def _Motor_Forward_():
	#print ' M2-L FOR;M1-R FOR; '
	XR.GPIOSet(XR.ENA)
	XR.GPIOSet(XR.ENB)
	XR.GPIOSet(XR.IN1)
	XR.GPIOClr(XR.IN2)
	XR.GPIOSet(XR.IN3)
	XR.GPIOClr(XR.IN4)
	XR.GPIOClr(XR.LED1)
	XR.GPIOClr(XR.LED2)
def _Motor_Backward_():
	#print ' M2-L REV;M1-R REV; '
	XR.GPIOSet(XR.ENA)
	XR.GPIOSet(XR.ENB)
	XR.GPIOClr(XR.IN1)
	XR.GPIOSet(XR.IN2)
	XR.GPIOClr(XR.IN3)
	XR.GPIOSet(XR.IN4)
	XR.GPIOSet(XR.LED1)
	XR.GPIOClr(XR.LED2)
def _Motor_TurnLeft_():
	#print ' M2-L REV;M1-R FOR; '
	XR.GPIOSet(XR.ENA)
	XR.GPIOSet(XR.ENB)
	XR.GPIOSet(XR.IN1)
	XR.GPIOClr(XR.IN2)
	XR.GPIOClr(XR.IN3)
	XR.GPIOSet(XR.IN4)
	XR.GPIOClr(XR.LED1)
	XR.GPIOSet(XR.LED2)
def _Motor_TurnRight_():
	#print ' M2-L FOR;M1-R REV; '
	XR.GPIOSet(XR.ENA)
	XR.GPIOSet(XR.ENB)
	XR.GPIOClr(XR.IN1)
	XR.GPIOSet(XR.IN2)
	XR.GPIOSet(XR.IN3)
	XR.GPIOClr(XR.IN4)
	XR.GPIOClr(XR.LED1)
	XR.GPIOSet(XR.LED2)
def _Motor_Stop_():
	#print ' M2-L STOP;M1-R STOP; '
	XR.GPIOClr(XR.ENA)
	XR.GPIOClr(XR.ENB)
	XR.GPIOClr(XR.IN1)
	XR.GPIOClr(XR.IN2)
	XR.GPIOClr(XR.IN3)
	XR.GPIOClr(XR.IN4)
	XR.GPIOSet(XR.LED1)
	XR.GPIOClr(XR.LED2)
##########机器人速度控制###########################
def _ENA_Speed_(EA_num):
	print ' M1_R速度变为 %d '%EA_num
	XR.ENAset(EA_num)

def _ENB_Speed_(EB_num):
	print ' M2_L速度变为 %d '%EB_num
	XR.ENBset(EB_num)

class Robot_Direction:
	def __init__(self):
		pass
		#self.motor_flag = motor_flag
	def forward(self):
		#print " Robot go forward %d"%motor_flag
		if ((glo.motor_flag == 1)or(glo.motor_flag == 2)):
			_Motor_Forward_()
		elif ((glo.motor_flag == 3)or(glo.motor_flag == 4)):
			_Motor_Backward_()
		elif ((glo.motor_flag == 5)or(glo.motor_flag == 6)):
			_Motor_TurnLeft_()
		elif ((glo.motor_flag == 7)or(glo.motor_flag == 8)):
			_Motor_TurnRight_()
	def back(self):
		#print " Robot go back"
		if ((glo.motor_flag == 1)or(glo.motor_flag == 2)):
			_Motor_Backward_()
		elif ((glo.motor_flag == 3)or(glo.motor_flag == 4)):
			_Motor_Forward_()
		elif ((glo.motor_flag == 5)or(glo.motor_flag == 6)):
			_Motor_TurnRight_()
		elif ((glo.motor_flag == 7)or(glo.motor_flag == 8)):
			_Motor_TurnLeft_()
	def left(self):
		#print " Robot turn left"
		if ((glo.motor_flag == 1)or(glo.motor_flag == 3)):
			_Motor_TurnLeft_()
		elif ((glo.motor_flag == 2)or(glo.motor_flag == 4)):
			_Motor_TurnRight_()
		elif ((glo.motor_flag == 5)or(glo.motor_flag == 7)):
			_Motor_Forward_()
		elif ((glo.motor_flag == 6)or(glo.motor_flag == 8)):
			_Motor_Backward_()
	def right(self):
		#print " Robot turn right"
		if ((glo.motor_flag == 1)or(glo.motor_flag == 3)):
			_Motor_TurnRight_()
		elif ((glo.motor_flag == 2)or(glo.motor_flag == 4)):
			_Motor_TurnLeft_()
		elif ((glo.motor_flag == 5)or(glo.motor_flag == 7)):
			_Motor_Backward_()
		elif ((glo.motor_flag == 6)or(glo.motor_flag == 8)):
			_Motor_Forward_()
	def stop(self):
		_Motor_Stop_()
	def M1_Speed(self,EA_num):
		_ENA_Speed_(EA_num)
	def M2_Speed(self,EB_num):
		_ENB_Speed_(EB_num)

