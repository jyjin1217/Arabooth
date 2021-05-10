from flask import Flask, render_template, request
import json
import requests
import sonoff_custom
import csv
import threading
from time import sleep

s = None;
devices = None;

application = Flask(__name__);

@application.route("/")
def home():
    return render_template("index.html");

@application.route("/iot_total")
def iot_total():
    return render_template("iot_total.html");

@application.route("/iot_new", methods=["POST","GET"])
def iot_new():
    # global s, devices;
    # if request.method == "POST":        
    #     device_id = devices[0]['deviceid'];
    #     swi = devices[0]['params']['switch'];
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

    #     devices = s.get_devices(False);
    #     #print(devices);
    #     print(devices[0]);
    
    return render_template("iot_new.html");

@application.route("/user_new", methods=["POST","GET"])
def user_new():
    csvResult = "";
    if request.method == "POST":
        fileLocate = request.form["fileLocate"];
        f = open(fileLocate, 'r', encoding='cp949');        
        csvText = csv.reader(f);        

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

    global s, devices;
    print(s);
    print(devices);

    return render_template("user_new.html", postResult=csvResult);


@application.route("/userMessage/<message>", methods=["POST","GET"])
def userMessage(message):
    print(message);

    msg = {};
    msg['msg'] = "server";
    mjson = json.dumps(msg);
    
    return mjson;


def loginSonoff():
    global s, devices;
    if s == None:
        s = sonoff_custom.Sonoff("iason78@naver.com", "koelceo5406!", "as");
    else:
        s.do_reconnect();
    
    devices = s.get_devices();

def thProc():
    while True:
        loginSonoff();
        sleep(60);

# th = threading.Thread(target=thProc);
# th.start();

if __name__ == "__main__":
    application.run(debug=True);





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
