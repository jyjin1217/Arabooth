from flask import Flask, render_template, request
import json
import requests
import sonoff_custom
import csv
import threading
from time import sleep
import os
from pymongo import MongoClient


#client = MongoClient('mongodb://mocha:mochamocha.@docdb-2021-05-11-05-38-41.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
#db = client.sample_database;
#print(client.list_database_names());
#col = db.sample_collection;
#col.insert_one({'hello':'Amazon DocumentDB'});
#x = col.find_one({'hello':'Amazon DocumentDB'});
#print(x);
#client.close();

s = None;
deviceDic = {};

application = Flask(__name__);

@application.route("/")
def home():
    return render_template("index.html");

@application.route("/iot_total")
def iot_total():
    return render_template("iot_total.html");

@application.route("/iot_new", methods=["POST","GET"])
def iot_new():
    # global s, deviceDic;
    # if request.method == "POST":        
    #     device_id = deviceDic[0]['deviceid'];
    #     swi = deviceDic[0]['params']['switch'];
    #     bb = not bb;
    #     if bb:
    #         s.switch("on", device_id, None); 
    #     else:
    #         s.switch("off", device_id, None);   
    # else:
    #     #s = sonoff_custom.Sonoff("jyjin1217@gmail.com", "2718059in", "as");
    #     if s == None:
    #         s = sonoff_custom.Sonoff("iason78@naver.com", "koelceo5406!", "as");
    #     else:
    #         s.do_reconnect();

    #     deviceDic = s.get_devices(False);
    #     #print(devices);
    #     print(deviceDic[0]);
    
    return render_template("iot_new.html");

@application.route("/user_new", methods=["POST","GET"])
def user_new():

    # 페이지에 던져줄 로그 string
    csvResult = "";

    if request.method == "POST":  
        # form에서 클릭하여 넘어온 값, 키는 속성 name이다      
        fileLocate = request.form["fileLocate"];

        # 경로값 분리 및 검사
        name, extenstion = os.path.splitext(fileLocate);
        if extenstion == "":
            csvResult = "Address must include file extension"
            return render_template("user_new.html", postResult=csvResult);
        elif extenstion != ".csv":
            csvResult = "Allowed file type is .csv file only"
            return render_template("user_new.html", postResult=csvResult);

        # 파일 오픈
        try:
            # 파일이 실제 존재하는지 검사
            # cp949로 encoding 해야 한글이 가능함
            f = open(fileLocate, 'r', encoding='cp949');
        except Exception as e:
            csvResult = e;
        else:
            # csv 파일 읽기
            csvText = csv.reader(f);

            # csv 파일 분석
            # aws dynamoDB 파일 Input

            topicList = [];
            isTopic = True;
            for line in csvText:            
                if isTopic :
                    for data in line:
                        topicList.append(data);
                    isTopic = False;
                    print(topicList);
                    continue;

                print(line);

            csvResult = "Hello";   

    return render_template("user_new.html", postResult=csvResult);


@application.route("/userMessage/<message>", methods=["POST","GET"])
def userMessage(message):
    global s, deviceDic;

    m = message.split(' ');
    returnMsg = {};
    returnMsg['msg'] = "Inappropriate Message";

    if m[0] == 'Work&All' and len(m) >= 4:
        if m[3] == "on" or m[3] == "off":
            if m[1] in deviceDic:
                if m[2] in deviceDic[m[1]]:
                    s.switch(m[3], deviceDic[m[1]][m[2]]); 
                    returnMsg['msg'] = "Dispatched";
    
    mjson = json.dumps(returnMsg);
    
    return mjson;

def loginSonoff():
    # ewelink 로그인
    global s, deviceDic;
    if s == None:
        s = sonoff_custom.Sonoff("iason78@naver.com", "koelceo5406!", "as");
    else:
        s.do_reconnect();
    
    # 디바이스 업데이트
    temp = s.get_devices();
    for device in temp:        
        dName = device['name'].split(' ');

        if dName[0] != 'Work&All':
            continue;
        if len(dName) < 3 :
            continue;        
                
        if dName[1] in deviceDic :
            deviceDic[dName[1]][dName[2]] = device['deviceid'];
        else:
            temDic = {};
            temDic[dName[2]] = device['deviceid'];
            deviceDic[dName[1]] = temDic;


def thProc():
    while True:
        loginSonoff();
        sleep(1800);

th = threading.Thread(target=thProc);
th.start();


# {
#     'settings': {
#         'opsNotify': 0,
#         'opsHistory': 1,
#         'alarmNotify': 1,
#         'wxAlarmNotify': 0,
#         'wxOpsNotify': 0,
#         'wxDoorbellNotify': 0,
#         'appDoorbellNotify': 1
#     },
#     'family': {
#         'id': '60586764ecbc07000893f705',
#         'index': 0
#     },
#     'group': '',
#     'online': True,
#     'groups': [],
#     'devGroups': [],
#     '_id': '6069228ad455080008fd6139',
#     'relational': [],
#     'deviceid': '10010c77b6',
#     'name': 'Sky_lounge',
#     'type': '10',
#     'apikey': 'd69672d5-7d17-4da3-bb84-c854570006c7',
#     'extra': {
#         'extra': {
#             'uiid': 1,
#             'description': '20201116003',
#             'brandId': '5c4c1aee3a7d24c7100be054',
#             'apmac': 'd0:27:02:18:ec:bd',
#             'mac': 'd0:27:02:18:ec:bc',
#             'ui': '单通道插座',
#             'modelInfo': '5c700f76cc248c47441fd234',
#             'model': 'PSF-B01-GL',
#             'manufacturer': '深圳松诺技术有限公司',
#             'chipid': '002BB02D',
#             'staMac': 'C4:DD:57:2B:B0:2D'
#         },
#         '_id': '5fb246d5348fba5c8da283b5'
#     },
#     'params': {
#         'version': 8,
#         'only_device': {
#             'ota': 'success'
#         },
#         'sledOnline': 'on',
#         'ssid': 'WA4F_24',
#         'bssid': '0e:00:00:00:00:00',
#         'switch': 'on',
#         'fwVersion': '3.5.0',
#         'rssi': -69,
#         'staMac': 'C4:DD:57:2B:B0:2D',
#         'startup': 'off',
#         'init': 1,
#         'pulse': 'off',
#         'pulseWidth': 500
#     },
#     'createdAt': '2021-04-04T02:20:58.645Z',
#     '__v': 0,
#     'onlineTime': '2021-05-06T00:41:03.837Z',
#     'ip': '116.124.50.130',
#     'location': '',
#     'tags': {
#         'm_06c7_iaso': 'on',
#         'm_d3eb_jyji': 'on',
#         'm_b9d7_123d': 'on',
#         'm_1ffe_insi': 'on'
#     },
#     'offlineTime': '2021-05-06T00:40:48.746Z',
#     'sharedTo': [
#         {
#             'phoneNumber': 'jyjin1217@gmail.com',
#             'permit': 15,
#             'note': ''
#         },
#         {
#             'phoneNumber': 'insidepark73@naver.com',
#             'permit': 15,
#             'note': ''
#         },
#         {
#             'phoneNumber': '123dltn123@naver.com',
#             'permit': 15,
#             'note': ''
#         }
#     ],
#     'devicekey': '74643c91-e802-487f-9ee5-70be102d136e',
#     'deviceUrl': 'https://as-api.coolkit.cc/api/detail/5c700f76cc248c47441fd234_en.html',
#     'brandName': 'SONOFF',
#     'showBrand': True,
#     'brandLogoUrl': 'https://as-ota.coolkit.cc/logo/q62PevoglDNmwUJ9oPE7kRrpt1nL1CoA.png',
#     'productModel': 'BASIC',
#     'devConfig': {},
#     'uiid': 1
# }
