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
