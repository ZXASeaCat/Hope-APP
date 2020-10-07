#解决问题，多个客户端发送数据，要怎么分开他们的全局变量：线程
#查询到底会怎么出错
#查询到底就发送一条，截止消息

from flask import Flask, render_template,request        # flask组件
from flask_socketio import SocketIO                     # flask-socketio
from MongodbHelper import MongodbHelper                 # MongoDB的数据访问类
from dateutil import parser                             # 转换器
from bson import json_util                              # 序列化Objectid
from threading import Lock                              # 线程
import time                                             # 时间
import pymongo 
from flask_cors import CORS




app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,cors_allowed_origins="*", async_mode=None)  # 很重要的设置
queryIndex = 0             # heart100表第一行是列名对应单位，第二行开始才是数据
eachQueryCount = 1000      # 每次查询数量
cursorMoveSteps = 6        # 每跨数行查询一次
patientData = {}           # 查询到的数据存储在这里

# patientData = MongodbHelper.queryCount("ECG","00001_20200101",limitCount=0,skipCount=0,cursorMoveSteps=10,fields={"_id":0})
# print(patientData.__len__())


# 打开IP地址
@app.route('/')
def index():
    global queryIndex
    queryIndex = 0
    return render_template('chart.html', async_mode=socketio.async_mode)


    
# 接收客户端的连接请求

@socketio.on('connect', namespace='/ecgdata')
def ecgdata_connect():
    global thread
    print("客户端已经连接")

    # 后台线程 产生数据，即刻推送至前端
    # 注意：这里不需要客户端连接的上下文，默认 broadcast = True
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(target=background_thread)

# 接收客户端的断开连接请求

@socketio.on('disconnect', namespace='/ecgdata')
def ecgdata_disconnect():
    global queryIndex
    global eachQueryCount
    global cursorMoveSteps
    global patientData
    queryIndex = 0            
    eachQueryCount = 1000     
    cursorMoveSteps = 6      
    patientData = {}          
    print("客户端断开连接")


################################
# 接收客户端的连接请求,发送病人心电信息
# parmas参数
# pt_id  病人ID      
# date   日期，格式：'YYYY-MM-DD'
################################
# patientECGInfo信息参数：
# "ecg_table": "00001_20200101",    心电表名字
# "fields": ["MKII", "V5"]          导联
################################
@socketio.on('getECGInfo', namespace='/ecgdata')
def test_connect(parmas):
    pt_id = parmas.get('pt_id')
    date = parmas.get('date')
    ret = MongodbHelper.query('LifeInfo','ecg_info',{'pt_id':pt_id,'date':parser.parse(date)},['ecg_table','fields'])
    socketio.emit('patientECGInfo',{"ecg_table":ret[0]["ecg_table"],"fields":ret[0]["fields"]},namespace='/ecgdata')


# 接收客户端的获取数据请求
@socketio.on('getECGData', namespace='/ecgdata')
def sendDataToClient(parmas):
    global queryIndex 
    global eachQueryCount
    global patientData
    # 这里游标采取步数为6，因为心电数据1秒采样大约333次，而客户端1秒最多60帧，所以333/60=6，每隔6行数据绘画一次
    patientData = MongodbHelper.queryECGCount("ECG",parmas.get('ecg_table'),eachQueryCount,queryIndex,cursorMoveSteps)
    # 将queryIndex定位到当前读取位置
    queryIndex = queryIndex + eachQueryCount * cursorMoveSteps
    socketio.emit('patientECGData',
                    {'patientData': patientData},
                    namespace='/ecgdata')

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",debug=True)  #代替了Flask自带的app.run()

# host="0.0.0.0",
# http://127.0.0.1:5000/getinfo/?pt_id=00001&&date=2020-07-17 



