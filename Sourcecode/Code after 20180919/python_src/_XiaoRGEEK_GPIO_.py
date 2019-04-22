#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
'''
文 件 名：_XiaoRGEEK_GPIO_.py
功    能：引脚定义及初始化文件,提供IO口操作函数以及调速函数。需要设置引脚为输入/输出模式。输出参考LED0设置，输入参考IR_R设置
外部条用：
import _XiaoRGEEK_GPIO_ as XR
XR.GPIOSet(XR.LED0)		#LED0引脚输出高电平
XR.GPIOClr(XR.LED0)		#LED0引脚输出低电平
XR.DigitalRead(IR_R)	#读取IR_R引脚状态
XR.ENAset(100)			#设置ENA占空比来调速，0-100之间
XR.ENBset(100)			#设置ENB占空比来调速，0-100之间
'''
import RPi.GPIO as GPIO
import time
#######################################
#############信号引脚定义##############
#######################################
########LED口定义#################
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
LED0 = 10
LED1 = 9
LED2 = 25
########电机驱动接口定义#################
ENA = 13	#//L298使能A
ENB = 20	#//L298使能B
IN1 = 19	#//电机接口1
IN2 = 16	#//电机接口2
IN3 = 21	#//电机接口3
IN4 = 26	#//电机接口4
########舵机接口定义#################
########超声波接口定义#################
ECHO = 4	#超声波接收脚位  
TRIG = 17	#超声波发射脚位
########红外传感器接口定义#################
IR_R = 18	#小车右侧巡线红外
IR_L = 27	#小车左侧巡线红外
IR_M = 22	#小车中间避障红外
IRF_R = 23	#小车跟随右侧红外
IRF_L = 24	#小车跟随左侧红外



#########led初始化为000##########
GPIO.setup(LED0,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED1,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED2,GPIO.OUT,initial=GPIO.HIGH)
#########电机初始化为LOW##########
GPIO.setup(ENA,GPIO.OUT,initial=GPIO.LOW)
ENA_pwm=GPIO.PWM(ENA,1000)
ENA_pwm.start(0)
ENA_pwm.ChangeDutyCycle(100)
GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ENB,GPIO.OUT,initial=GPIO.LOW)
ENB_pwm=GPIO.PWM(ENB,1000)
ENB_pwm.start(0)
ENB_pwm.ChangeDutyCycle(100)
GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)
#########红外初始化为输入，并内部拉高#########
GPIO.setup(IR_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_M,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
##########超声波模块管脚类型设置#########
GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)#超声波模块发射端管脚设置trig
GPIO.setup(ECHO,GPIO.IN,pull_up_down=GPIO.PUD_UP)#超声波模块接收端管脚设置echo




'''
def	GPIO_setup():
#########led初始化为000##########
	GPIO.setup(LED0,GPIO.OUT,initial=GPIO.HIGH)
	GPIO.setup(LED1,GPIO.OUT,initial=GPIO.HIGH)
	GPIO.setup(LED2,GPIO.OUT,initial=GPIO.HIGH)
#########电机初始化为LOW##########
	ENA_Setup().ENA_init()
	GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
	ENB_Setup().ENB_init()
	GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)
#########红外初始化为输入，并内部拉高#########
	GPIO.setup(IR_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(IR_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(IR_M,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(IRF_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(IRF_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
##########超声波模块管脚类型设置#########
	GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)#超声波模块发射端管脚设置trig
	GPIO.setup(ECHO,GPIO.IN,pull_up_down=GPIO.PUD_UP)#超声波模块接收端管脚设置echo
'''
def	GPIOSet(gpio):
	GPIO.output(gpio,True)

def	GPIOClr(gpio):
	GPIO.output(gpio,False)
def	DigitalRead(gpio):
	return GPIO.input(gpio)
def ENAset(EA_num):
	ENA_pwm.ChangeDutyCycle(EA_num)
def ENBset(EB_num):
	ENB_pwm.ChangeDutyCycle(EB_num)





