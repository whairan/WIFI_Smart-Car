#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_FUNC_Pathdec_.py
功    能：XiaoRGEEK摄像头循迹功能，需要
外部调用：
import _XiaoRGEEK_FUNC_Pathdec_ as PATdec
PATdec.Path_Dect()
PATdec.Path_Dect_img_processing()
'''
import time
import _XiaoRGEEK_GPIO_ as XR
import _XiaoRGEEK_GLOBAL_variable_ as G_val
from _XiaoRGEEK_MOTOR_ import Robot_Direction
go = Robot_Direction()
import cv2
import numpy as np

####################################################
##函数名称 Path_Dect()
##函数功能 ：摄像头巡线电机控制函数
##入口参数 ：FF130800FF，摄像头调试，FF130801FF开始摄像头循迹
##出口参数 
#int Path_Dect_px 	平均像素坐标
#int Path_Dect_on	1:开始循迹，0停止循迹
####################################################
def	Path_Dect():
	while (G_val.Path_Dect_on):
		print 'Path_Dect_px %d '%G_val.Path_Dect_px	 #打印巡线中心点坐标值
		if (G_val.Path_Dect_px < 260)&(G_val.Path_Dect_px > 0):	#如果巡线中心点偏左，就需要左转来校正。
			print("turn left")
			go.left()
		elif G_val.Path_Dect_px> 420:
			print("turn right")
			go.right()
		else :
			go.forward()
			print("go stright")
		time.sleep(0.007)
		go.stop()
		time.sleep(0.006)
####################################################
##函数名称 Path_Dect_img_processing()
##函数功能 ：摄像头巡线图像处理函数
##入口参数 ：FF130800FF，摄像头调试，FF130801FF开始摄像头循迹
##出口参数 
#int Path_Dect_px 	平均像素坐标
#int Path_Dect_on	1:开始循迹，0调试模式/停止循迹
####################################################
def	Path_Dect_img_processing():
	Path_Dect_fre_count = 1
	Path_Dect_px_sum = 0
	Path_Dect_cap = 0
	print("into theads Path_Dect_img_processing")
	while True:
		if(G_val.Path_Dect_on):
			if(Path_Dect_cap == 0):
				cap = cv2.VideoCapture(0)
				Path_Dect_cap = 1
			else:
				ret,frame = cap.read()	#capture frame_by_frame
				gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #get gray img
				if (G_val.Path_Dect_Flag == 0):
					ret,thresh1=cv2.threshold(gray,70,255,cv2.THRESH_BINARY)		#巡黑色线
				else :
					ret,thresh1=cv2.threshold(gray,70,255,cv2.THRESH_BINARY_INV)	#巡白色线
				for j in range(0,640,5):
					if thresh1[240,j] == 0:
						Path_Dect_px_sum = Path_Dect_px_sum + j
						Path_Dect_fre_count = Path_Dect_fre_count + 1 
				G_val.Path_Dect_px =  (Path_Dect_px_sum)/ (Path_Dect_fre_count)
				Path_Dect_px_sum = 0
				Path_Dect_fre_count = 1
		elif(Path_Dect_cap):
			go.stop()
			time.sleep(0.001)
			Path_Dect_cap = 0
			cap.release()
		time.sleep(0.1)