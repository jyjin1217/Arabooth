from flask import Flask, render_template, request, send_file
import json
import requests
import sonoff_custom
import csv
import threading
from time import sleep
import os
from pymongo import MongoClient
import sys

s = None;
deviceDic = {};

application = Flask(__name__);

# 대시보드 페이지
@application.route("/")
def home():
    return render_template("index.html");

# 테이블 페이지
@application.route("/user_total")
def user_total():
    return render_template("user_total.html");

# 테이블 페이지
@application.route("/iot_total")
def iot_total():
    return render_template("iot_total.html");

# 신규디바이스 등록 페이지
@application.route("/iot_new", methods=["POST","GET"])
def iot_new():
    if request.method == "POST":
        pass;
        # client = MongoClient("arabooth.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017", username="mocha", password="mochamocha.", ssl="true")
        
        # client = MongoClient('mongodb://mocha:mochamocha.@arabooth.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=C:\\Users\\jyjin\\Desktop\\ParkingB\\aws\\rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
        # client = MongoClient('mongodb://mocha:mochamocha.@arabooth.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
        # client = MongoClient('mongodb://mocha:mochamocha.@docdb-2021-05-11-05-38-41.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
        # client = MongoClient('mocha:mochamocha.@docdb-2021-05-11-05-38-41.cluster-cnnzidmnwuis.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
        # print(client);
        # db = client.sample_database;
        # print(db);
        # col = db.sample_collection;
        # print(col);
        # col.insert_one({'hello':'Amazon DocumentDB'});
        # x = col.find_one({'hello':'Amazon DocumentDB'});
        # print(x);
        # client.close();



        # print(client.list_database_names());
        
    
    return render_template("iot_new.html");

# 신규유저 등록 페이지
@application.route("/user_new", methods=["POST","GET"])
def user_new():

    # 페이지에 던져줄 로그용 string
    csvResult = "";

    if request.method == "POST":  
        # post 버튼 판별, 버튼에 따라 다른 기능 부여
        rType = "delete";
        if request.form.get('addOne') or request.form.get('addAll'):
            rType = "insert";
        
        isAll = True;
        if request.form.get('addOne') or request.form.get('delOne'):
            isAll = False;
        
        totalDic = {}; # 실제 저장하게될 데이터 dic
        isOk = True; # 저장에 문제가 없을지 검출

        # csv파일로 데이터베이스 변경
        if isAll :
            # 파일이 존재하는지 확인
            if not request.files.get("file"):
                isOk = False;
                csvResult = "No file to upload";
                        
            # 올바른 파일(csv)인지 걸러내기
            if isOk:
                f = request.files["file"];
                cType = f.content_type;
                
                extension = cType.split('.');
                if extension[len(extension) - 1] != "ms-excel":
                    csvResult = "File extension is not match. Must be csv file";
                    isOk = False;
            
            # csv파일 확인시
            if isOk:
                f = request.files["file"];
                fd = f.read().decode("cp949").splitlines();

                #reader = csv.reader(fd); # 리스트 style
                reader = csv.DictReader(fd); # 딕셔너리 style

                # 리스트로 변경(검사를 위함)
                dicList = list(reader); 

                # 내용물 검사
                if len(dicList) > 0:
                    # 키값(Topic) 검사
                    if not (dicList[0].get('개인ID') and dicList[0].get('회원명') and dicList[0].get('연락처') and dicList[0].get('회사명') and dicList[0].get('호점')):
                        isOk = False;
                        csvResult = "Key value is not matched. You should check your csv file"
                else:
                    isOk = False;
                    csvResult = "There are no data in file";
                
                # 데이터 담기
                if isOk:
                    nameKey = 0; # 별개의 object 이름 부여용도
                    for data in dicList:
                        # 스킵 조건
                        if data.get("서비스타입"):
                            if data["서비스타입"] == "퇴실회원":
                                continue;
                        
                        temDic = {};
                        temDic['id'] = data["개인ID"];
                        temDic['name'] = data["회원명"];
                        temDic['phone'] = data["연락처"];
                        temDic['company'] = data["회사명"];
                        temDic['locate'] = data["호점"];
                        temDic['type'] = rType;

                        curName = "obj" + str(nameKey);
                        nameKey += 1;
                        totalDic[curName] = temDic;
            
        # 개별 정보로 데이터베이스 변경
        else:
            if not (request.form.get('newId') and request.form.get('newName') and request.form.get('newPhone') and request.form.get('newCompany') and request.form.get('newLocate')):                
                csvResult = "Data is not filled. You should fill all data";
                isOk = False;

            if isOk:
                temDic = {}; # total에 담을 개별 dic
                temDic['id'] = request.form['newId'];
                temDic['name'] = request.form['newName'];
                temDic['phone'] = request.form['newPhone'];
                temDic['company'] = request.form['newCompany'];
                temDic['locate'] = request.form['newLocate'];
                temDic['type'] = rType;
                totalDic['obj'] = temDic;

        # 데이터에 문제가 없다 판단시에만 저장 진행
        if isOk:
            # Aws ApiGateway 전달
            awsEndpoint = 'https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/conndb'
            msgJson = json.dumps(totalDic)
            requests.request('POST', awsEndpoint, data=msgJson)
            csvResult = "Success. Data is delivered"

    return render_template("user_new.html", postResult=csvResult);

# sample Excel 문서 다운로드
@application.route("/sampleDown")
def downloadDample():
    return send_file("static/sample.xlsx");


# 외부유저(mobile) 요청(iot control), <message> 규칙: 'Work&All 지역명 구분이름 on/off'
@application.route("/userMessage/<message>", methods=["POST","GET"])
def userMessage(message):
    global s, deviceDic;

    m = message.split(' ');
    returnMsg = {};
    returnMsg['msg'] = "Failed";    

    if s == None:
        loginSonoff();

    counting = 0;
    while counting < 5: 
        if len(m) == 3:
            if m[2] == "on" or m[2] == "off":
                if m[0] in deviceDic:
                    if m[1] in deviceDic[m[0]]: 
                        result = s.switch(m[2], deviceDic[m[0]][m[1]]);
                        if result:
                            returnMsg['msg'] = "Dispatched";
                            break;
                        else:
                            returnMsg['detail'] = "RequestFail";
                            loginSonoff();
                            counting += 1;
                    else:
                        returnMsg['detail'] = "NoneMatch";
                        loginSonoff();
                        counting += 1;
                else:
                    returnMsg['detail'] = "NoneMatch";
                    loginSonoff();
                    counting += 1;
            else:
                returnMsg['detail'] = "WrongMessage";
                break;
        else:
            returnMsg['detail'] = "WrongMessage";
            break;


    return json.dumps(returnMsg);

def loginSonoff():
    # ewelink 로그인
    global s, deviceDic;
    if s == None:
        s = sonoff_custom.Sonoff("contact5@worknall.com", "opentoday21!", "as");
    else:
        s.do_reconnect();
    
    # 디바이스 업데이트, 디바이스 이름 규칙: 'Work&All 지역명 구분이름'
    temp = s.get_devices();
    for device in temp:        
        dName = device['name'].split(' ');
        
        if len(dName) < 2 :
            continue;        
                
        if dName[0] in deviceDic :
            deviceDic[dName[0]][dName[1]] = device['deviceid'];
        else:
            temDic = {};
            temDic[dName[1]] = device['deviceid'];
            deviceDic[dName[0]] = temDic;


    


# 쓰레드 함수, 일정 시간마다 ewelink 재로그인 및 디바이스 업데이트
def thProc():
    while True:
        loginSonoff();
        sleep(1800);

# 쓰레드 실행
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
