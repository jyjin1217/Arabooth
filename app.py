from flask import Flask, render_template, request
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
            # 올바른 파일(csv)인지 걸러내기 to do


            # csv파일이라면
            if isOk:
                file = request.files["file"];
                file_data = file.read().decode("cp949");

                isTopic = True; # 첫줄(topic) 걸러내기 및 키값 확인
                keyDic = {}; # topic 컬럼번호를 저장할 dic
                keyCount = 0; # 현재 컬럼체크
                temStr = ""; # 각 컬럼 문자 정보
                isSkip = False; # 스킵 여부

                
                temDic = {}; # total에 담을 개별 dic
                nameKey = 0; # 별개의 object 이름 부여용도

                for curStr in file_data:
                    # 한 라인 종료 (= topic 종료 or 한명의 데이터 종료)
                    if curStr == '\n':  

                        keyCount = 0;
                        temStr = ""; # isSkip이 일어났을 시, 뒤쪽 데이터가 쌓여있을 수 있기 때문

                        if isTopic:
                            isTopic = False;
                            # 필요한 키값이 다 존재하지 않을 시, 진행 종료
                            if not (keyDic.get('개인ID') and keyDic.get('회원명') and keyDic.get('연락처') and keyDic.get('회사명') and keyDic.get('호점')) :
                                csvResult = "Key value is not matched. You should check your csv file";
                                isOk = False;
                                break;

                            # 반드시 필요하지는 않기에, 없을시에는 로직오류를 없애기 위해 대입
                            if not keyDic.get('서비스타입'):
                                keyDic['서비스타입'] = -1;

                        else:
                            if isSkip:
                                isSkip = False;
                            else:
                                # 실제 저장할 데이터로써 total에 담기
                                curName = "obj" + str(nameKey);
                                nameKey += 1;
                                temDic['type'] = rType;
                                totalDic[curName] = temDic;
                                temDic = {};

                    # 한 컬럼 종료
                    elif curStr == ',':

                        if isSkip:
                            continue;

                        if isTopic:
                            if temStr == '개인ID':
                                keyDic['개인ID'] = keyCount;
                            elif temStr == '회원명':
                                keyDic['회원명'] = keyCount;
                            elif temStr == '연락처':
                                keyDic['연락처'] = keyCount;
                            elif temStr == '회사명':
                                keyDic['회사명'] = keyCount;
                            elif temStr == '호점':
                                keyDic['호점'] = keyCount;
                            elif temStr == '서비스타입':
                                keyDic['서비스타입'] = keyCount;
                        else:
                            if keyCount == keyDic['개인ID']:
                                temDic['id'] = temStr;
                            elif keyCount == keyDic['회원명']:
                                temDic['name'] = temStr;
                            elif keyCount == keyDic['연락처']:
                                temDic['phone'] = temStr;
                            elif keyCount == keyDic['회사명']:
                                temDic['company'] = temStr;
                            elif keyCount == keyDic['호점']:
                                temDic['locate'] = temStr;
                            elif keyCount == keyDic['서비스타입']:
                                if temStr == '퇴실회원':
                                    isSkip = True;                                

                        keyCount += 1;
                        temStr = "";

                    # 개별 문자 저장
                    else:
                        temStr += curStr;
                

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

        if isOk:
            # Aws ApiGateway 전달
            awsEndpoint = 'https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/conndb'
            msgJson = json.dumps(totalDic)
            requests.request('POST', awsEndpoint, data=msgJson)
            csvResult = "Data is delivered"


        # # 경로값 분리 및  확장자 검사
        # name, extenstion = os.path.splitext(fileLocate);
        # if extenstion == "":
        #     csvResult = "Address must include file extension"
        #     return render_template("user_new.html", postResult=csvResult);
        # elif extenstion != ".csv":
        #     csvResult = "Allowed file type is .csv file only"
        #     return render_template("user_new.html", postResult=csvResult);


    return render_template("user_new.html", postResult=csvResult);


# 외부유저(mobile) 요청(iot control), <message> 규칙: 'Work&All 지역명 구분이름 on/off'
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
    
    # 디바이스 업데이트, 디바이스 이름 규칙: 'Work&All 지역명 구분이름'
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
    


# 쓰레드 함수, 일정 시간마다 ewelink 재로그인 및 디바이스 업데이트
def thProc():
    while True:
        loginSonoff();
        sleep(1800);

# 쓰레드 실행
# th = threading.Thread(target=thProc);
# th.start();

if __name__ == "__main__":
    application.run(debug=True);
    # application.run();




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
