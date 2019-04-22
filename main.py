'''
    养猫
'''
import asyncio
import aiohttp
import xml.dom.minidom
from openpyxl import Workbook
import requests
import sys
import os
import random
import other.cookie.cookie
import json
from struct import *
import threading
import re
import time
from socket import *


class my_Tool():
    def __init__(self):
        try:
            config_object = open('./systemdata/systemdata.json',mode='r',encoding = "utf-8")
            config = json.loads(config_object.read(),encoding = "utf-8")
            self.roomid = config['data']['roomid']
            self.systemday = config['data']['systemday']
            self.instruction = config['data']['instruction']
            self.control = re.findall(r'{(.+?),', self.instruction )
            self.controlFlag = re.findall(r',(\w+?)}', self.instruction )
            self.out("i",str(self.control))
            self.out("i",str(self.controlFlag))
            config_object.close()
            
            file_object = open('./other/cookie/cookies.json',mode='r')
            cookie = json.loads(file_object.read())
            self._token = cookie['bili_jct']
            cookie = str(cookie)
            cookie = cookie.replace(': ', '=')
            cookie = cookie.replace('\'', '')
            cookie = cookie.replace('{', '')
            cookie = cookie.replace('}', '')
            cookie = cookie.replace(' ', '')
            cookie = cookie.replace(',', '; ')
            self._cookie = cookie
            file_object.close()
        except:
            self.out ('i','my_Tool_init错误')
            self.restart_program()
    
    #控制台输出与日志保存
    def out(self,grade,text):
        f = open('./log/'+grade+'/'+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'.log','a')
        f.write(time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))+'  '+text+'\n')
        f.close()
        print(text)

    #异常重启
    def restart_program(self):
        self.out('e',"程序重启中...")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    #数据更新
    def config(self):
        while(1):
            try:
                config_object = open('./systemdata/systemdata.json',mode='r',encoding = "utf-8")
                config = json.loads(config_object.read(),encoding = "utf-8")
                
                if self.roomid != config['data']['roomid'] :
                    myTool.out ('e','系统数据被修改')
                    self.restart_program()
                if self.instruction != config['data']['instruction'] :
                    self.instruction = config['data']['instruction']
                    self.control = re.findall(r'{(.+?),', self.instruction )
                    self.controlFlag = re.findall(r',(\w+?)}', self.instruction )
                if config['data']['systemday'] != time.strftime('%Y-%m-%d',time.localtime(time.time())) :
                    myTool.out ('i','次日数据更新')
                    #更新账号cookie
                    mycookt = threading.Thread(target=myClient.mycook,)
                    mycookt.start()
                    config['data']['systemday'] = time.strftime('%Y-%m-%d',time.localtime(time.time())) 
                    self.systemday = time.strftime('%Y-%m-%d',time.localtime(time.time())) 
                    with open('./systemdata/systemdata.json', 'w',encoding = "utf-8") as f:
                        json.dump(config,f,ensure_ascii=False)
                    f.close()
                    config_object.close()
                    continue
                
                clientSend_object = open('./tool/clientSend.json',mode='r',encoding = "utf-8")
                clientSend = json.loads(clientSend_object.read(),encoding = "utf-8")
                
                if clientSend['data']['flag'] != 100:
                    myTool.out('i','1')
                    if clientSend['data']['flag'] == 0:
                        myClient.type = clientSend['data']['TCP_server_barrage']['type']
                        myClient.barrage = clientSend['data']['TCP_server_barrage']['barrage']
                        myClient.nick = clientSend['data']['TCP_server_barrage']['nick']
                        myClient.sid = clientSend['data']['TCP_server_barrage']['sid']
                        myClient.giftNum = clientSend['data']['TCP_server_barrage']['giftNum']
                        myClient.source = clientSend['data']['TCP_server_barrage']['source']
                        myClient.openId = clientSend['data']['TCP_server_barrage']['optId']
                        myClient.TCP_client_send()
                    elif clientSend['data']['flag'] == 1:
                        myClient.type = clientSend['data']['TCP_server_gift']['type']
                        myClient.barrage = clientSend['data']['TCP_server_gift']['barrage']
                        myClient.nick = clientSend['data']['TCP_server_gift']['nick']
                        myClient.sid = clientSend['data']['TCP_server_gift']['sid']
                        myClient.giftNum = clientSend['data']['TCP_server_gift']['giftNum']
                        myClient.source = clientSend['data']['TCP_server_gift']['source']
                        myClient.openId = clientSend['data']['TCP_server_gift']['optId']
                        myClient.TCP_client_send()
                    clientSend['data']['flag'] = 100
                    myTool.out('i','1')
                    with open('./tool/clientSend.json', 'w',encoding = "utf-8") as f:
                        json.dump(clientSend,f,ensure_ascii=False)
                    f.close()
                    clientSend_object.close()
                    continue
                    
                clientSend_object.close()
                config_object.close()
                time.sleep(1)
            except:
                myTool.out('e','数据更新出错')
                time.sleep(1)
                continue
        
class my_Client():
    def __init__(self):
        config_object = open('./systemdata/systemdata.json',mode='r',encoding = "utf-8")
        config = json.loads(config_object.read(),encoding = "utf-8")
        self.client_IP = config['data']['TCP_client']['IP']
        self.client_PORT = config['data']['TCP_client']['PORT']
        self.server_IP = config['data']['TCP_server']['IP']
        self.server_PORT = config['data']['TCP_server']['PORT']
        config_object.close()
            
        self.control_msg = ""
        #control_msg ->控制指令(查阅systemdata.json   data.instruction)
        self.msg = ""
        #msg ->扩展接口
            
        self.type = ""
        #type ->类型：1礼物 0弹幕 2娃娃机-申请上机 3娃娃机-操作 4查询抓取结果
        self.barrage = ""
        #barrage ->弹幕内容
        self.giftNum = ""
        #giftNum ->礼物数量
        self.nick = ""
        #nick ->用户ID
        self.sid = ""
        #sid ->用户昵称
        self.source = ""
        #source ->用户所在视频站：1-bilibili 2-斗鱼
        self.openId = ""
        #openId ->每个指令的专有ID
        self.playOptId = ""
        #playOptId ->操作娃娃需传入optId，申请上机成功的时候会返回optId
        
        self.ZB = ""
        #Wawaji的坐标
        self.WawajiStartEnd = 0
        #Wawaji的上机成功标志位
        self.WawajiActEnd = ""
        #Wawaji的运行完成标志位
        self.WawajiCXEnd = ""
        #Wawaji的结果反馈完成标志位
    #更新cookie
    def mycook(self):
        other.cookie.cookie.main()
        file_object = open('./other/cookie/cookies.json',mode='r')
        cookies = json.loads(file_object.read())
        danmuji._token = cookies['bili_jct']
        cookies = str(cookies)
        cookies = cookies.replace(': ', '=')
        cookies = cookies.replace('\'', '')
        cookies = cookies.replace('{', '')
        cookies = cookies.replace('}', '')
        cookies = cookies.replace(' ', '')
        cookies = cookies.replace(',', '; ')
        danmuji._cookie = cookies
        myTool.out('i',"更新cookie")

    #更新Wawaji
    def Wawaji(self):
        try:
            myTool.out('i',self.ZB)
            wawanick = self.nick
            wawasid = self.sid
            wawagiftNum = self.giftNum
            
            wawasource = self.source
            wawaopenId = self.openId
                
            #申请上机
            strtcp = "{\
                        \"type\": " + '2' + ",\
                        \"barrage\": \"" + "申请上机" + "\",\
                        \"nick\": \"" + str(wawanick) + "\",\
                        \"sid\": \"" + str(wawasid) + "\",\
                        \"giftNum\": " + str(wawagiftNum) + ",\
                        \"source\": " + str(wawasource) + ",\
                        \"optId\": " + str(wawaopenId) + ",\
                        \"playOptId\": " + str(self.playOptId) + "\
                    }\n"
            self.WawajiStartEnd = 0
            strtcp = strtcp.replace(' ','')
            myTool.out("i",strtcp)
            self.tctimeClient.send(strtcp.encode("gbk"))
            while(1):
                time.sleep(0.1)
                if self.WawajiStartEnd == 1:
                    danmuji.send_message("@" + str(wawanick) + "正在抓取" + str(self.ZB))
                    break
                if self.WawajiStartEnd == 2:
                    danmuji.send_message("@" + wawanick + "余额不足，赠送任意礼物即可控制")
                    return
                if self.WawajiStartEnd == 3:
                    danmuji.send_message("@" + wawanick + "机器被占用")
                    return
            #抓取娃娃
            strtcp = "{\
                        \"type\": " + '3' + ",\
                        \"barrage\": \"" + str(self.ZB) + "\",\
                        \"nick\": \"" + str(wawanick) + "\",\
                        \"sid\": \"" + str(wawasid) + "\",\
                        \"giftNum\": " + str(wawagiftNum) + ",\
                        \"source\": " + str(wawasource) + ",\
                        \"optId\": " + "31" + ",\
                        \"playOptId\": " + str(self.playOptId) + "\
                    }\n"
            strtcp = strtcp.replace(' ','')
            self.WawajiActEnd = 0
            myTool.out("i",strtcp)
            self.tctimeClient.send(strtcp.encode("gbk"))
            
            while(1):
                time.sleep(0.1)
                if self.WawajiActEnd == 1:
                    break
            
            self.WawajiCXEnd = 0
            strtcp = "{\
                        \"type\": " + '4' + ",\
                        \"barrage\": \"" + str(self.ZB) + "\",\
                        \"nick\": \"" + str(wawanick) + "\",\
                        \"sid\": \"" + str(wawasid) + "\",\
                        \"giftNum\": " + str(wawagiftNum) + ",\
                        \"source\": " + str(wawasource) + ",\
                        \"optId\": " + "32" + ",\
                        \"playOptId\": " + str(self.playOptId) + "\
                    }\n"
            strtcp = strtcp.replace(' ','')
            myTool.out("i",strtcp)
            while(1):
                #查询结果
                self.tctimeClient.send(strtcp.encode("gbk"))
                time.sleep(1)
                if self.WawajiCXEnd == 2:
                    danmuji.send_message("恭喜" + str(wawanick) + "获得10000喵币奖励" )
                    self.type = "1"
                    self.barrage = "娃娃"
                    self.giftNum = 1
                    self.nick = wawanick
                    self.sid = wawasid
                    self.source = 1
                    self.openId = "20"
                    self.TCP_client_send()
                    break
                if self.WawajiCXEnd == 1:
                    danmuji.send_message("@" + str(wawanick) + "未抓到娃娃，继续努力哟" )
                    break
        except :
            myTool.out('e',"Wawaji运行异常")
        finally:
            myTool.out('i',"Wawaji运行完成")
            self.WawajiStartEnd = 0
            self.WawajiActEnd = 0
            self.WawajiCXEnd = 0
            self.type = ""
            self.barrage = ""
            self.giftNum = ""
            self.nick = ""
            self.sid = ""
            self.source = ""
            self.openId = ""
            self.playOptId = ""
            self.ZB = ""
        
        
    # TCP_server
    def TCP_server(self):
        try:
            BUFSIZ = 1024
            ADDR = (self.server_IP, self.server_PORT)
            self.tcpSerSock = socket(AF_INET, SOCK_STREAM)   #创建套接字
            self.tcpSerSock.bind(ADDR)   #绑定IP和端口
            self.tcpSerSock.listen(5)    #监听端口，最多5人排队
            
            while True:
                try:
                    myTool.out('i','server等待连接')
                    self.tcpCliSock, addr = self.tcpSerSock.accept()    #建立连接
                    myTool.out('i','server接收到 '+ str(addr)+' 的连接')
                
                    while True:
                        #接收来自client的数据
                        self.serverdata = self.tcpCliSock.recv(BUFSIZ)
                        if not self.serverdata:
                            myTool.out('e',"TCP_server断开")
                            break
                except :
                    myTool.out ('i','server出错')
            self.tcpSerSock.close()
        except :
            myTool.out('e',"TCP_server运行异常")
            self.tcpSerSock.close()
            time.sleep(1)
            self.TCP_server()

    # TCP_client
    def TCP_client(self):
        try:
            BUFFSIZE=2048
            ADDR = (self.client_IP,self.client_PORT)
            myTool.out('i','client开始连接')
            self.tctimeClient = socket(AF_INET,SOCK_STREAM)
            self.tctimeClient.connect(ADDR)
            myTool.out('i',"TCP_client连接成功")
            
            while True:
                try:
                    #接收来自server的数据
                    self.clientdata = self.tctimeClient.recv(BUFFSIZE).decode("gbk")
                    myTool.out('i',"client接收到：" + str(self.clientdata))
                    if not self.clientdata:
                        myTool.out('e',"TCP_client断开")
                        break
                    self.clientdata = self.clientdata.replace(' ','')
                    self.clientdata = self.clientdata.replace('\n','')
                    self.clientdata = json.loads(self.clientdata)
                    
                    #弹幕
                    if self.clientdata['data']['type'] == 0:
                        for s in range(0, len(myTool.control)):
                            if self.clientdata['data']['barrage'] == myTool.control[s]:
                                if self.clientdata['data']['control'] == 1:
                                    self.control_msg = myTool.controlFlag[s]
                                    self.msg = ""
                                    self.TCP_server_send()
                                    danmuji.send_message('主播接收到指令,正在执行')
                                if self.clientdata['data']['control'] == 0:
                                    danmuji.send_message('余额不足，赠送任意礼物即可控制')
                        if self.clientdata['data']['barrage'] == '我的余额':
                            danmuji.send_message('@' + str(self.clientdata['data']['nick']) + '用户余额为' + str(self.clientdata['data']['balance']))
                    
                    #礼物
                    if self.clientdata['data']['type'] == 1:
                        myTool.out('i',"礼物")
                        pass
                    
                    #Wawaji上机申请
                    if self.clientdata['data']['type'] == 2:
                        if self.clientdata['data']['control'] == 1:
                            myTool.out('i',"Wawaji上机申请")
                            self.playOptId = self.clientdata['data']['playOptId']
                            self.WawajiStartEnd = 1
                        if self.clientdata['data']['control'] == 0:
                            if self.clientdata['msg'] == "申请上机失败":
                                self.WawajiStartEnd = 3
                            self.WawajiStartEnd = 2
                        pass
                        
                    #Wawaji运行完成
                    if self.clientdata['data']['type'] == 3:
                        myTool.out('i',"Wawaji运行完成")
                        self.WawajiActEnd = 1
                        pass
                        
                    #Wawaji反馈完成
                    if self.clientdata['data']['type'] == 4 :
                        if self.clientdata['data']['result'] == 1 :
                            myTool.out('i',"Wawaji反馈完成")
                            self.WawajiCXEnd = 2
                        if self.clientdata['data']['result'] == 0 :
                            myTool.out('i',"Wawaji反馈完成")
                            self.WawajiCXEnd = 1
                        pass
                    
                except :
                    myTool.out ('i','client出错')
            self.tctimeClient.close()
            self.TCP_client()
        except :
            myTool.out('e',"TCP_client运行异常")
            self.tctimeClient.close()
            time.sleep(1)
            self.TCP_client()

    # TCP_server_send
    def TCP_server_send(self):
        try:
            strtcp = "{\"control_msg\":\""+ str(self.control_msg) + "\",\"msg\":\""+"\"}\n"
            self.control_msg = ""
            self.msg = ""
            self.tcpCliSock.send(strtcp.encode("utf-8"))
        except :
            myTool.out('e',"TCP_server_send运行异常")

    # TCP_client_send
    def TCP_client_send(self):
        try:
            strtcp = "{\
                        \"type\": " + str(self.type) + ",\
                        \"barrage\": \"" + str(self.barrage) + "\",\
                        \"nick\": \"" + str(self.nick) + "\",\
                        \"sid\": \"" + str(self.sid) + "\",\
                        \"giftNum\": " + str(self.giftNum) + ",\
                        \"source\": " + str(self.source) + ",\
                        \"optId\": " + str(self.openId) + "\
                    }\n"
            strtcp = strtcp.replace(' ','')
            myTool.out("i",strtcp)
            self.type = ""
            self.barrage = ""
            self.giftNum = ""
            self.nick = ""
            self.sid = ""
            self.source = ""
            self.openId = ""
            self.tctimeClient.send(strtcp.encode("gbk"))
        except :
            myTool.out('e',"TCP_client_send运行异常")
            

class bilibiliClient():
    def __init__(self):
        self._CIDInfoUrl = 'http://live.bilibili.com/api/player?id=cid:'
        self._roomId = 0
        self._ChatPort = 788
        self._protocolversion = 1
        self._reader = 0
        self._writer = 0
        self.connected = False
        self._UserCount = 0
        self._ChatHost = 'livecmt-1.bilibili.com'
        self._cookie = "rpdid=olwwiopsmkdospwimilww; buvid3=A7BCE4AE-B75B-4CAC-AB99-2AFD29E95D2919603infoc; fts=1540274964; sid=czoam3es; _ga=GA1.2.1278657130.1541655164; UM_distinctid=166f1de340f788-033311c7c0ef99-65381e55-1fa400-166f1de3410416; LIVE_BUVID=56b03375f04a411ba265be17f6a821d8; LIVE_BUVID__ckMd5=a53c7221ddf85fd8; finger=81df3ec0; im_notify_type_24749829=0; DedeUserID=393446305; DedeUserID__ckMd5=9c30648b917019da; SESSDATA=42b8db00%2C1549094723%2Cd7ba9b11; bili_jct=9a85a8c05d8f63f23a3194b5e7834e00; LIVE_PLAYER_TYPE=1; bp_t_offset_393446305=207344369465877591; CURRENT_QUALITY=0; CURRENT_FNVAL=16; stardustvideo=1; _dfcaptcha=85a0eafcf5925bf5f1b3d3bcf61500a7"
        self._token = ""
        self._instruction = ""
        self.tcpCliSock = ""
        self.error = 0
        
        
        file_object = open('./other/cookie/cookies.json',mode='r')
        cookies = json.loads(file_object.read())
        self._token = cookies['bili_jct']
        cookies = str(cookies)
        cookies = cookies.replace(': ', '=')
        cookies = cookies.replace('\'', '')
        cookies = cookies.replace('{', '')
        cookies = cookies.replace('}', '')
        cookies = cookies.replace(' ', '')
        cookies = cookies.replace(',', '; ')
        self._cookie = cookies
        
    async def connectServer(self,room):
        try:
            self._roomId = room
            self._roomId = int(self._roomId)
            
            #获取房间页面文本,通过正则表达获取真正的房间ID
            async with aiohttp.ClientSession() as session:
                async with session.get('http://live.bilibili.com/' + str(self._roomId)) as r:
                    html = await r.text()
                    m = re.findall(r'"room_id":(\d+)', html)
                    ROOMID = m[0]
                self._roomId = int(ROOMID)
                async with session.get(self._CIDInfoUrl + ROOMID) as r:
                    xml_string = '<root>' + await r.text() + '</root>'
                    dom = xml.dom.minidom.parseString(xml_string)
                    root = dom.documentElement
                    server = root.getElementsByTagName('server')
                    self._ChatHost = server[0].firstChild.data

            reader, writer = await asyncio.open_connection(self._ChatHost, self._ChatPort)
            self._reader = reader
            self._writer = writer
            if (await self.SendJoinChannel(self._roomId) == True):
                self.connected = True
                await self.ReceiveMessageLoop()
        except:
            myTool.out ('e','SendJoinChannelwhile错误')
            myTool.restart_program()

    #房间心跳
    async def HeartbeatLoop(self):
        try:
            t = 0
            while self.connected == False:
                t = t+1
                await asyncio.sleep(0.5)
                if(t == 15):
                    myTool.out ('e',"心跳出错")
                    myTool.restart_program()
            try:
                while self.connected == True:
                    await self.SendSocketData(0, 16, self._protocolversion, 2, 1, "")
                    await asyncio.sleep(15)
            except: # 发生异常直接退出该 task
                myTool.out ('i',"----停止心跳")
                return
        except:
            myTool.out ('e',"心跳出错")
            myTool.restart_program()

    #接入房间
    async def SendJoinChannel(self, channelId):
        try:
            self._uid = (int)(100000000000000.0 + 200000000000000.0*random.random())
            body = '{"roomid":%s,"uid":%s}' % (channelId, self._uid)
            await self.SendSocketData(0, 16, self._protocolversion, 7, 1, body)
            return True
        except:
            myTool.out ('e',"SendJoinChannel出错")
            myTool.restart_program()

    #发送数据
    async def SendSocketData(self, packetlength, magic, ver, action, param, body):
        try:
            bytearr = body.encode('utf-8')
            if packetlength == 0:
                packetlength = len(bytearr) + 16
            sendbytes = pack('!IHHII', packetlength, magic, ver, action, param)
            if len(bytearr) != 0:
                sendbytes = sendbytes + bytearr
            self._writer.write(sendbytes)
            await self._writer.drain()
        except:
            myTool.out ('e',"SendSocketData出错")
            restart_program()

    #接收数据
    async def ReceiveMessageLoop(self):
        self.barrage_list = []
        self.gift_list = []
        
        while self.connected == True:
            try:

                self.m = re.findall(r'{(.+?),', self._instruction )
                self.n = re.findall(r',(\w+?)}', self._instruction )
                
                tmp = await self._reader.read(4)
                expr, = unpack('!I', tmp)
                tmp = await self._reader.read(2)
                tmp = await self._reader.read(2)
                tmp = await self._reader.read(4)
                num, = unpack('!I', tmp)
                tmp = await self._reader.read(4)
                num2 = expr - 16

                if num2 != 0:
                    num -= 1
                    if num==0 or num==1 or num==2:
                        tmp = await self._reader.read(4)
                        num3, = unpack('!I', tmp)
                        myTool.out ('i','房间人数为 %s' % num3)
                        self._UserCount = num3
                        continue
                    elif num==3 or num==4:
                        tmp = await self._reader.read(num2)
                        # strbytes, = unpack('!s', tmp)
                        try: # 为什么还会出现 utf-8 decode error??????
                            messages = tmp.decode('utf-8')
                        except:
                            continue
                        self.parseDanMu(messages)
                        continue
                    elif num==5 or num==6 or num==7:
                        tmp = await self._reader.read(num2)
                        continue
                    else:
                        if num != 16:
                            tmp = await self._reader.read(num2)
                        else:
                            continue
            except:
                myTool.out ('e',"ReceiveMessageLoop出错")
                restart_program()
                continue

    #弹幕信息处理函数
    def parseDanMu(self, messages):
        try:
            try:
                dic = json.loads(messages)
            except: # 有些情况会 jsondecode 失败，未细究，可能平台导致
                myTool.out ('e',"获取json失败")
                return
            cmd = dic['cmd']
            
            #弹幕
            if cmd == 'DANMU_MSG':
                commentText = dic['info'][1]
                commentUser = dic['info'][2][1]
                commentUserid = dic['info'][2][0]
                isAdmin = dic['info'][2][2] == '1'
                isVIP = dic['info'][2][3] == '1'
                myTool.out ('i',commentUser + ' ' + commentText)
                if commentText[0] != '#':
                    try:
                        if commentText[0:1] == '抓' and commentText[1] == 'x' and commentText[3] == 'y':
                            if (int(commentText[2]) < 9 and int(commentText[2]) >= 0) and (int(commentText[4]) < 9 and int(commentText[4]) >= 0):
                                #线程：Wawaji
                                if myClient.ZB == "":
                                    try:
                                        myClient.ZB = str(commentText[1:5])
                                        myClient.barrage = commentText
                                        myClient.nick = commentUser
                                        myClient.sid = commentUserid
                                        myClient.giftNum = 0
                                        myClient.source = 1
                                        myClient.openId = "30"
                                        myClient.playOptId = "0"
                                        Wawaji =threading.Thread(target=myClient.Wawaji,)
                                        Wawaji.start()
                                    except:
                                        myClient.ZB = ""
                                        pass
                                return
                    except:
                        pass
                
                    self.recall_message(commentText)
                    myClient.type = "0"
                    myClient.barrage = commentText
                    myClient.nick = commentUser
                    myClient.sid = commentUserid
                    myClient.giftNum = 0
                    myClient.source = 1
                    myClient.openId = "10"
                    myClient.TCP_client_send()
                return

            #礼物
            if cmd == 'SEND_GIFT' :
                GiftName = dic['data']['giftName']
                GiftUser = dic['data']['uname']
                Giftrcost = dic['data']['rcost']
                GiftNum = int(dic['data']['num'])
                Giftuid = dic['data']['uid']
                myTool.out ('i',GiftUser + '送出' + GiftName)
                self.send_message("谢" + GiftUser + '送出的' + GiftName)
                myClient.type = "1"
                myClient.barrage = GiftName
                myClient.nick = GiftUser
                myClient.sid = Giftuid
                myClient.giftNum = GiftNum
                myClient.source = 1
                myClient.openId = "20"
                myClient.TCP_client_send()
                
                return
            
            #欢迎
            if cmd == 'WELCOME' :
                commentUser = dic['data']['uname']
                try:
                    pass
                except:
                    myTool.out('e',"WELCOME失败")
                return
            return
        except:
            myTool.out ('e',"弹幕处理出错")
            return
    
    #发送弹幕
    def send_message(self,str):
        try:
            again_str = ''
            if len(str) > 19:
                send_message_again_flag = 1
                again_str = str[19:len(str)+1]
                str = str[0:19]
            roomid = self._roomId
            url_send = 'https://api.live.bilibili.com/msg/send'
            data = {
                'color': '16777215',
                'fontsize': '25',
                'mode': '1',
                'msg': '#' + str,
                'rnd': int(time.time()),
                'roomid': roomid,
                'bubble':0,
                'csrf_token': self._token,
                'csrf':self._token
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                'Cookie': self._cookie
            }
            try:
                html_send = requests.post(url_send, data=data, headers=headers)
                result = json.loads(html_send.text)
                
                if result['msg'] == '你被禁言啦':
                    myTool.out('i','您被禁言啦!!! 跟随弹幕发送失败~')
                    time.sleeep(0.2)
                    self.send_message(str)
                if result['msg'] == 'msg repeat':
                    myTool.out('i','重复发送')
                    time.sleeep(0.2)
                    self.send_message(" " + str)
                if result['code'] == 0 and result['msg'] == '':
                    myTool.out('i','')
                    
                else:
                    myTool.out('e','弹幕发送失败')
                if again_str != '':
                    time.sleep(0.5)
                    self.send_message(again_str)
            except:
                myTool.out('e','弹幕发送出错')
            time.sleep(0.5)
        except:
            myTool.out('e','send_message出错')
    #弹幕回复
    def recall_message(self,str):
        data_object = open('./data/data.json',mode='r',encoding = "utf-8")
        mydata = json.loads(data_object.read(),encoding = "utf-8")
        data_object.close()
        myTool.out ('i',mydata['data']['recall']['flag'])
        if mydata['data']['recall']['flag'] in str:
            self.send_message(mydata['data']['recall']['re'])

myClient = my_Client()
myTool = my_Tool()
danmuji = bilibiliClient()
if __name__ == '__main__':
    try:
        myTool.out ('i','main.py启动成功')
        while(os.system('ping www.baidu.com')):
            time.sleep(1)
            myTool.out ('e','网络链接失败')
    
        #线程：实时更新数据
        config =threading.Thread(target=myTool.config,)
        config.start()
    
        #线程：TCP_client
        TCP_client =threading.Thread(target=myClient.TCP_client,)
        TCP_client.start()
    
        #线程：TCP_server
        TCP_server =threading.Thread(target=myClient.TCP_server,)
        TCP_server.start()
        
        #线程：弹幕实时抓取
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait([
            danmuji.connectServer(myTool.roomid) ,
            danmuji.HeartbeatLoop()
        ]))
        
        while(1):
            time.sleep(10000)
            pass
    except:
        myTool.out('e',"主程序运行异常")
        myTool.restart_program()