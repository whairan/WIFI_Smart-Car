/*
树莓派WiFi无线视频小车机器人驱动源码（C版本）
作者：XIAO-R团队
版本信息：wifirobots.c  2017.11.08
版本号	：V1.0
版权所有：小R科技（深圳市小二极客科技有限公司）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
*/

#include <wiringPi.h>
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <softPwm.h>
#include <ctype.h>
#include <wiringPiI2C.h>
#include "libXRservo.h"

int LED0 = 12;				//定义LED0引脚
int LED1 = 13;				//定义LED1引脚
int LED2 = 6;				//定义LED2引脚
int ENA = 23;				//定义电机使能A引脚
int ENB = 28;				//定义电机使能B引脚
int IN1 = 24;				//定义电机引脚1
int IN2 = 27;				//定义电机引脚2
int IN3 = 29;				//定义电机引脚3
int IN4 = 25;				//定义电机引脚4

int IR_L = 1;				//小车左侧巡线红外
int IR_R = 2;				//小车右侧巡线红外
int IR_M = 3;				//小车中间避障红外
int IRF_R = 4;				//小车跟随右侧红外
int IRF_L = 5;				//小车跟随左侧红外

int ECHO = 7;				//超声波接收脚位  
int TRIG = 0;				//超声波发射脚位

int fd = 0;
int adjust = 0;				//电机顺序校准参数
int Cruising_Flag = 0;		//模式切换标志
int Pre_Cruising_Flag = 0;	//记录上次模式
int ServoStatusLED = 0;		//舵机指示灯状态位
int pwmAcount = 0;			//pwmA计数
int pwmBcount = 0;			//pwmB计数
int SpeedLeft = 4000;		//电机左侧速度值
int SpeedRight = 4000;		//电机右侧速度值
int LastSpeedLeft = 4000;	//上次电机左侧速度值
int LastSpeedRight = 4000;	//上次电机右侧速度值
#define MOTOR_GO_FORWARD	{digitalWrite(IN1,LOW);digitalWrite(IN2,HIGH);digitalWrite(IN3,LOW);digitalWrite(IN4,HIGH);}	//车体前进                          
#define MOTOR_GO_BACK		{digitalWrite(IN1,HIGH);digitalWrite(IN2,LOW);digitalWrite(IN3,HIGH);digitalWrite(IN4,LOW);}	//车体后退
#define MOTOR_GO_RIGHT		{digitalWrite(IN1,HIGH);digitalWrite(IN2,LOW);digitalWrite(IN3,LOW);digitalWrite(IN4,HIGH);}	//车体右转
#define MOTOR_GO_LEFT		{digitalWrite(IN1,LOW);digitalWrite(IN2,HIGH);digitalWrite(IN3,HIGH);digitalWrite(IN4,LOW);}	//车体左转
#define MOTOR_GO_STOP		{digitalWrite(IN1,LOW);digitalWrite(IN2,LOW);digitalWrite(IN3,LOW);digitalWrite(IN4,LOW);}		//车体停止

#define PORT		2001		//定义服务器端口号
#define BACKLOG		1			//设置请求队列的最大长度
#define MAXRECVLEN	1024		//一次读取的缓存数

#define AvoidLength	15			//超声波避障的距离

char data[MAXRECVLEN];		//数据接收缓存
int Hex_data[MAXRECVLEN];	//数据接收缓存byte
int buffer[3]={0};			//协议数据缓存
char Sendbuf[5]={0};			//发送数据缓存
char IPaddr[] = "192.168.1.1";//定义服务器IP地址
int listenfd, connectfd;	//socket描述
struct sockaddr_in server;	//服务端地址信息
struct sockaddr_in client;	//客户端地址信息
socklen_t addrlen;			//客户端数量


/*
通过校准值校准小车方向
*/ 
void forward(int adjust)
{
	switch (adjust)
	{
		case 1: MOTOR_GO_FORWARD;	return;
		case 2: MOTOR_GO_FORWARD;	return;
		case 3: MOTOR_GO_BACK;		return;
		case 4: MOTOR_GO_BACK;		return;
		case 5: MOTOR_GO_LEFT;		return;
		case 6: MOTOR_GO_LEFT;		return;
		case 7: MOTOR_GO_RIGHT;		return;
		case 8: MOTOR_GO_RIGHT;		return;
		default: return;
	}
}
/*
通过校准值校准小车方向
*/ 
void back(int adjust)
{
	switch (adjust)
	{
		case 1: MOTOR_GO_BACK;		return;
		case 2: MOTOR_GO_BACK;		return;
		case 3: MOTOR_GO_FORWARD;	return;
		case 4: MOTOR_GO_FORWARD;	return;
		case 5: MOTOR_GO_RIGHT;		return;
		case 6: MOTOR_GO_RIGHT;		return;
		case 7: MOTOR_GO_LEFT;		return;
		case 8: MOTOR_GO_LEFT;		return;
		default: return;
	}
}
/*
通过校准值校准小车方向
*/ 
void left(int adjust)
{
	switch (adjust)
	{
		case 1: MOTOR_GO_LEFT;		return;
		case 2: MOTOR_GO_RIGHT;		return;
		case 3: MOTOR_GO_LEFT;		return;
		case 4: MOTOR_GO_RIGHT;		return;
		case 5: MOTOR_GO_FORWARD;	return;
		case 6: MOTOR_GO_BACK;		return;
		case 7: MOTOR_GO_FORWARD;	return;
		case 8: MOTOR_GO_BACK;		return;
		default: return;
	}
}
/*
通过校准值校准小车方向
*/ 
void right(int adjust)
{
	switch (adjust)
	{
		case 1: MOTOR_GO_RIGHT;		return;
		case 2: MOTOR_GO_LEFT;		return;
		case 3: MOTOR_GO_RIGHT;		return;
		case 4: MOTOR_GO_LEFT;		return;
		case 5: MOTOR_GO_BACK;		return;
		case 6: MOTOR_GO_FORWARD;	return;
		case 7: MOTOR_GO_BACK;		return;
		case 8: MOTOR_GO_FORWARD;	return;
		default: return;
	}
}



/*####################################################
##函数名称 ：Open_Light()
##函数功能 ：开大灯LED0
##入口参数 ：无
##出口参数 ：无
####################################################*/
void Open_Light()
{
	digitalWrite(LED0,LOW);
}

/*####################################################
##函数名称 ：Close_Light()
##函数功能 ：关大灯
##入口参数 ：无
##出口参数 ：无
####################################################*/
void Close_Light()
{
	digitalWrite(LED0,HIGH);
}
 

/*
*********************************************************************************************************
** 函数名称 ：Avoiding
** 函数功能 ：检测在车体前面中间方位红外前有无障碍，有的话小车停止
** 入口参数 ：无
** 出口参数 ：无
*********************************************************************************************************
*/  
void Avoiding()//红外避障函数
{
	if ((digitalRead(IR_M) == LOW))
	{
		MOTOR_GO_STOP;//停止
	}
}

/*
*********************************************************************************************************
** 函数名称 ：Follow
** 函数功能 ：跟随模式,检测黑线在俩个红外之间的位置，通过逻辑判断再做出小车的方向改变
** 入口参数 ：无
** 出口参数 ：无
*********************************************************************************************************
*/
void Follow()	//跟随模式
{
	int ir_m= digitalRead(IR_M);
	int irf_l = digitalRead(IRF_L);
	int irf_r = digitalRead(IRF_R);
	if(ir_m == HIGH)	//中间传感器没有探测到物体
	{
		if((irf_l == LOW)&& (irf_r == LOW)){		//俩边同时探测到物体
			MOTOR_GO_STOP;		//停止 
		} 
		if((irf_l == LOW)&& (irf_r == HIGH)){		//左侧探测到物体
			left(adjust);		//左转 
		}
		if((irf_l == HIGH)&& (irf_r == LOW)){		//右侧探测到物体
			right(adjust);		//右转
		}
		if((irf_l == HIGH)&& (irf_r == HIGH)){		//探测到无任何物体
			forward(adjust);	//直行 
		}
	}
	else{
		MOTOR_GO_STOP;
	}
}


/*####################################################
##函数名称 ：TrackLine()
##函数功能 ：巡线模式,检测黑线在俩个红外之间的位置，
			通过逻辑判断再做出小车的方向改变
##入口参数 ：无
##出口参数 ：无
####################################################*/
void TrackLine()	// 巡线模式
{
	SpeedLeft = 1300;	//巡线时速度不应太快
	SpeedRight = 1300;
	int ir_m = digitalRead(IR_M);
	int ir_l = digitalRead(IR_L);		//读取左边传感器数值
	int ir_r = digitalRead(IR_R);		//读取右边传感器数值
	if(ir_m == HIGH) //中间传感器没有探测到物体
	{
		if ((ir_l == HIGH) && (ir_r == HIGH)){	//左右都检测到，就如视频中的那样遇到一道横的胶带
			MOTOR_GO_STOP;		//停止
		}
		if ((ir_l == HIGH) && (ir_r == LOW)){	//左侧遇到黑线
			left(adjust);		//左转
		}
		if ((ir_l == LOW) && ( ir_r == HIGH)){	//右侧遇到黑线
			right(adjust);		//右转
		}
		if ((ir_l == LOW) && ( ir_r == LOW)){	//俩边都没有检测到黑线表明在轨迹中
			forward(adjust);	//直行
		}
	}
	else{
		MOTOR_GO_STOP;
	}
}

/*####################################################
##函数名称 Get_Distance()
##函数功能 ：超声波测出距离
##入口参数 ：无
##出口参数 ：dis
####################################################*/
float Get_Distance()
{
	struct timeval t1;
	struct timeval t2;
	long start, stop;
	float dis;
	long timeout = 0;

	digitalWrite(TRIG, LOW);					//先拉低发射引脚
	delayMicroseconds(2);
	digitalWrite(TRIG, HIGH);					//拉高发射引脚
	delayMicroseconds(10);						//发出超声波脉冲至少10us脉冲信号
	digitalWrite(TRIG, LOW);					//拉低发射引脚

	while(!(digitalRead(ECHO) == 1))			//ECHO引脚检测高电平
	{
		timeout++;
		if(timeout>10000000)return 0;			//超时处理
	}
	gettimeofday(&t1, NULL);					//获取当前时间  
	timeout = 0;
	while(!(digitalRead(ECHO) == 0))			//ECHO引脚检测低电平
	{
		timeout++;
		if(timeout>10000000)return 0;			//超时处理
	}
	gettimeofday(&t2, NULL);					//获取当前时间  

	start = t1.tv_sec * 1000000 + t1.tv_usec;	//微秒级的时间  
	stop  = t2.tv_sec * 1000000 + t2.tv_usec;

	dis = (float)(stop-start)/1000000*34000/2;	//求出距离  

	return dis;
}

/*####################################################
##函数名称 ：AvoidByRadar()
##函数功能 ：超声波避障
##入口参数 ：distance
##出口参数 ：无
####################################################*/
void AvoidByRadar(int distance)
{
	float leng = Get_Distance();
	if(distance<10)distance=10;    //限定最小避障距离为10cm
	if((leng>2)&&(leng < distance))//避障距离值(单位cm)，大于1是为了避免超声波的盲区
	{
		while((Get_Distance()>1)&&(Get_Distance() < distance))
		{
			back(adjust);
		}
		MOTOR_GO_STOP;
	}
}

/*####################################################
##函数名称 ：Send_Distance()
##函数功能 ：超声波距离PC端显示
##入口参数 ：distance
##出口参数 ：无
####################################################*/
void Send_Distance()
{
	int dis= Get_Distance();
	Sendbuf[0]=0xff;
	Sendbuf[1]=0x03;
	Sendbuf[2]=0x00;
	Sendbuf[3]=dis;
	Sendbuf[4]=0xff;
	send(connectfd, Sendbuf, 5, 0);
	delay(1000);
}


/*####################################################
##函数名称 ：Communication_Decode()
##函数功能 ：串口指令解析函数
##入口参数 ：无
##出口参数 ：无
####################################################*/
void Communication_Decode()
{
	if(buffer[0]==0x00)
	{
		switch(buffer[1])	//电机命令
		{
			case 0x01:MOTOR_GO_FORWARD;digitalWrite(LED2,LOW);	return;
			case 0x02:MOTOR_GO_BACK;digitalWrite(LED2,LOW);		return;
			case 0x03:MOTOR_GO_RIGHT;digitalWrite(LED2,LOW);	return;
			case 0x04:MOTOR_GO_LEFT;digitalWrite(LED2,LOW);		return;
			case 0x00:MOTOR_GO_STOP;digitalWrite(LED2,HIGH);	return;
			default: return;
		}
	}
	else if (buffer[0] == 0x01) //舵机命令
	{
		ServoStatusLED=!ServoStatusLED;	//舵机状态灯翻转
		digitalWrite(LED1,ServoStatusLED);
		if (buffer[2] > 175)return;
		XiaoRGEEK_SetAngle(fd,buffer[1],buffer[2]);
	}
	else if (buffer[0] == 0x02)		//调速
	{
		if (buffer[2] > 100)return;
		if (buffer[1] == 0x01){		//左侧调档
			LastSpeedLeft=SpeedLeft=30*buffer[2]+1000;			//速度档位是0~100 换算成pwm 速度pwm低于1000电机不转
		}
		if (buffer[1] == 0x02){		//右侧调档
			LastSpeedRight=SpeedRight=30*buffer[2]+1000;		//速度档位是0~100 换算成pwm 速度pwm低于1000电机不转
		}
	}
	
	else if (buffer[0] == 0x32) //保存舵机角度
	{
		XiaoRGEEK_SaveServo(fd);	return;
	}
	
	else if (buffer[0] == 0x33) //读取舵机角度并赋值
	{
		XiaoRGEEK_ReSetServo(fd);	return;
	}
	
	else if (buffer[0] == 0x04)//开车灯指令为FF040000FF,关车灯指令为FF040100FF
	{
		switch (buffer[1])  
		{
			case 0x00: Close_Light(); return;	//关车灯 
			case 0x01: Open_Light(); return;	//开车灯
			default: return;
		}
	}
	
	else if (buffer[0] == 0x05)//读取电压 FF050000FF
	{
		if (buffer[1] == 0x00)  
		{
			int Val = XiaoRGEEK_ReadVol(fd);
			printf("Read_Voltage: %d",Val);
		}
	}
	
	else if (buffer[0] == 0x06)//读取脉冲 FF060000FF读取脉冲1号  FF060100FF读取脉冲2号
	{
		if (buffer[1] == 0x00)
		{
			int Speed1 = XiaoRGEEK_SpeedCounter1(fd);
			printf("Read_Speed1: %d",Speed1);
		}
		else
		{
			int Speed2 = XiaoRGEEK_SpeedCounter2(fd);
			printf("Read_Speed2: %d",Speed2);
		}
	}
	
	else if (buffer[0] == 0x40)	//存储电机标志
	{
		adjust = buffer[1];
	}
	
	else if (buffer[0] == 0x13)	//模式切换开关
	{
		SpeedLeft = LastSpeedLeft;
		SpeedRight = LastSpeedRight;
		switch (buffer[1])
		{
			case 0x01: Cruising_Flag = 1; return;	//跟随模式
			case 0x02: Cruising_Flag = 2;return;	//巡线模式
			case 0x03: Cruising_Flag = 3;return;	//避障模式
			case 0x04: Cruising_Flag = 4;return;	//雷达避障模式
			case 0x05: Cruising_Flag = 5;return;	//超声波距离PC端显示
			default: Cruising_Flag = 0;return;		//正常模式
		}
	}
}


/*####################################################
##函数名称 ：*pwmTheard
##函数功能 ：电机PWM产生线程,1KHZ
##入口参数 ：无
##出口参数 ：无
####################################################*/
void *pwmTheard()
{
	while(1)
	{
		if(pwmAcount<=SpeedLeft){
			digitalWrite(ENA,HIGH);
		}
		else{
			digitalWrite(ENA,LOW);
		}
		if(pwmBcount<=SpeedRight){
			digitalWrite(ENB,HIGH);
		}
		else{
			digitalWrite(ENB,LOW);
		}
		pwmAcount++;
		pwmBcount++;
		if(pwmAcount>4000)pwmAcount=0;
		if(pwmBcount>4000)pwmBcount=0;
	}
}

/*####################################################
##函数名称 ：*dataTheard
##函数功能 ：数据线程处理函数
##入口参数 ：无
##出口参数 ：无
####################################################*/
void *dataTheard()
{
	while(1)
	{
		if((connectfd=accept(listenfd,(struct sockaddr *)&client, &addrlen))==-1)
		{
			perror("accept() error. \n");
			exit(1);
		}
		struct timeval tv;
		gettimeofday(&tv, NULL);
		printf("You got a connection from client's ip %s, port %d at time %ld.%ld\n",inet_ntoa(client.sin_addr),htons(client.sin_port), tv.tv_sec,tv.tv_usec);

		int iret=0;
		int rec_flag=0;
		int rec_count=0;
		while(1)
		{
			iret = recv(connectfd, data, MAXRECVLEN, 0);
			//data[iret] ='\0';
			if(iret>0)
			{
				//StrToHex(data,Hex_data,(iret/2));
				for(int i=0;i<iret;i++)        
				{
					Hex_data[i] = (int)data[i];
					if(!rec_flag)
					{
						if(Hex_data[i]==0xff)//第一次获取到0xff(即包头)
						{
							rec_flag=1;
							rec_count=0;
						}
					}
					else
					{
						if(Hex_data[i]==0xff)//第二次获取到0xff(即包尾)
						{
							rec_flag = 0;
							if(rec_count==3)//获取到中间数据为3个字节，说明此命令格式正确
							{
								Communication_Decode(); //执行命令解析函数
							}
							rec_count = 0;
						}
						else
						{
							buffer[rec_count]=Hex_data[i];//暂存数据
							rec_count++;
						}
					}
				}
			}
			else
			{
				close(connectfd);
				break;
			}
			/* print client's ip and port */
			//send(connectfd, data, iret, 0); /* send to the client welcome message */
		}
	}
	close(listenfd); /* close listenfd */
}

/*####################################################
##函数名称 ：thread_create
##函数功能 ：创建线程函数
##入口参数 ：无
##出口参数 ：无
####################################################*/
void thread_create()
{
	if((piThreadCreate(*dataTheard)) != 0){	//判断线程是否创建成功
		printf("thread 1 create fail!\n");
	}
	else{
		printf("thread 1 create success!\n");
	}
	if((piThreadCreate(*pwmTheard)) != 0){	//判断线程是否创建成功
		printf("thread 2 create fail!\n");
	}
	else{
		printf("thread 2 create success!\n");
	}
}


/*####################################################
##函数名称 ：init_server
##函数功能 ：创建TCP服务器
##入口参数 ：无
##出口参数 ：无
####################################################*/
void init_server()
{
	//创建一个TCP socket
	if ((listenfd = socket(AF_INET, SOCK_STREAM, 0)) == -1)//判断socket是否创建成功
	{
		/* handle exception */
		perror("socket() error. Failed to initiate a socket");
		exit(1);
	}
	//设置Socket
	int opt = SO_REUSEADDR;
	setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
	bzero(&server, sizeof(server));
	server.sin_family = AF_INET;
	server.sin_port = htons(PORT);//指定端口
	server.sin_addr.s_addr= inet_addr(IPaddr);//指定IP地址
	if(bind(listenfd, (struct sockaddr *)&server, sizeof(server)) == -1)
	{
		/* handle exception */
		perror("Bind() error.");
		exit(1);
	}
	if(listen(listenfd, BACKLOG) == -1)
	{
		perror("listen() error. \n");
		exit(1);
	}
	addrlen = sizeof(client);
	thread_create();
}


/*####################################################
##函数名称 init_light()
##函数功能 流水灯
##入口参数 ：无
##出口参数 ：无
####################################################*/
void init_light()
{
	for(int i=0;i<=5;i++)
	{
		digitalWrite(LED0,HIGH);//流水灯LED0
		digitalWrite(LED1,HIGH);//流水灯LED1
		digitalWrite(LED2,HIGH);//流水灯LED2
		delay(200);
		digitalWrite(LED0,LOW); //流水灯LED0
		digitalWrite(LED1,HIGH);//流水灯LED1
		digitalWrite(LED2,HIGH);//流水灯LED2
		delay(200);
		digitalWrite(LED0,HIGH);//流水灯LED0
		digitalWrite(LED1,LOW); //流水灯LED1
		digitalWrite(LED2,HIGH);//流水灯LED2
		delay(200);
		digitalWrite(LED0,HIGH);//流水灯LED0
		digitalWrite(LED1,HIGH);//流水灯LED1
		digitalWrite(LED2,LOW); //流水灯LED2
		delay(200);
		digitalWrite(LED0,HIGH);//流水灯LED0
		digitalWrite(LED1,HIGH);//流水灯LED1
		digitalWrite(LED2,HIGH);//流水灯LED2
		delay(200);
	}
	for(int i=0;i<=5;i++)
	{
		digitalWrite(LED0,LOW); //流水灯LED0
		digitalWrite(LED1,LOW); //流水灯LED1
		digitalWrite(LED2,LOW); //流水灯LED2
		delay(300);
		digitalWrite(LED0,HIGH);//流水灯LED0
		digitalWrite(LED1,HIGH);//流水灯LED1
		digitalWrite(LED2,HIGH);//流水灯LED2
		delay(300);
	}
	digitalWrite(LED0,LOW); //流水灯LED0
	digitalWrite(LED1,LOW); //流水灯LED1
	digitalWrite(LED2,LOW); //流水灯LED2
}


/*####################################################
##函数名称 ：Cruising_Mod()
##函数功能 : 模式切换
##入口参数 ：无
##出口参数 ：无
####################################################*/
void Cruising_Mod()//模式功能切换函数
{
	if (Pre_Cruising_Flag != Cruising_Flag)
	{
		if (Pre_Cruising_Flag != 0)
		{
			MOTOR_GO_STOP;
		}
		Pre_Cruising_Flag =  Cruising_Flag;
	}
	switch (Cruising_Flag)
	{
		case 1: Follow(); return;					//跟随模式
		case 2: TrackLine(); return; 				//巡线模式
		case 3: Avoiding(); return;					//避障模式
		case 4: AvoidByRadar(AvoidLength); return;	//超声波避障模式
		case 5: Send_Distance(); return; 			//超声波距离PC端显示
		default: return;
	}
}

/*####################################################
##函数名称 ：Setup()
##函数功能 ：初始化
##入口参数 ：无
##出口参数 ：无
####################################################*/
void Setup()
{
	wiringPiSetup();			//初始化GPIO
	pinMode(LED0,OUTPUT);		//LED0设置为输出
	pinMode(LED1,OUTPUT);		//LED1设置为输出
	pinMode(LED2,OUTPUT);		//LED2设置为输出
	pinMode(ENA,OUTPUT);		//使能A设置为输出
	pinMode(ENB,OUTPUT);		//使能B设置为输出
	pinMode(IN1,OUTPUT);		//电机引脚1设置为输出
	pinMode(IN2,OUTPUT);		//电机引脚2设置为输出
	pinMode(IN3,OUTPUT);		//电机引脚3设置为输出
	pinMode(IN4,OUTPUT);		//电机引脚4设置为输出
	pinMode(IR_R,INPUT);		//右侧巡线红外设置为输入
	pinMode(IR_L,INPUT);		//左侧巡线红外设置为输入
	pinMode(IR_M,INPUT);		//中间避障红外设置为输入
	pinMode(IRF_R,INPUT);		//右侧跟随红外设置为输入
	pinMode(IRF_L,INPUT);		//左侧跟随红外设置为输入
	pinMode(ECHO,INPUT);		//超声波模块发射端管脚echo设置输入
	pinMode(TRIG,OUTPUT);		//超声波模块发射端管脚trig设置输出
	digitalWrite(ENA,HIGH);		//使能A设置为输出
	digitalWrite(ENB,HIGH);		//使能B设置为输出
	init_light();				//流水灯
	init_server();				//启动TCP服务器
	fd = XiaoRGEEK_InitServo();	//初始化舵机
}

/*####################################################
##函数名称 ：main()
##函数功能 ：主函数
##入口参数 ：无
##出口参数 ：无
####################################################*/
int main(void)
{
	Setup();
	while(1)
	{
		Cruising_Mod();
	}
}