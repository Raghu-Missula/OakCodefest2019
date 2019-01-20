import pandas as pd
import time, random, math
import pygal
import numpy.polynomial.polynomial as poly
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, redirect, url_for, request
from io import StringIO

conv_msg = {}

DEGREE = 8

def find_close_idx(array, val):
    for idx in range(len(array)):
        obj = array[idx]
        if obj < val and array[idx+1] > val:
            return (idx, idx+1)
        elif obj == val:
            return (idx, idx)
    return (idx,idx)

def comparison(x_array_mn, y_array_mn, x_array_avg, y_array_avg):
    output = []
    for idx in range(len(x_array_mn)):
        x_val = x_array_mn[idx]
        y_val = y_array_mn[idx]
        (low_lim_idx,high_lim_idx) = find_close_idx(x_array_avg,x_val)
        if low_lim_idx == high_lim_idx:
            y_avg = y_array_avg[low_lim_idx]
        else:
            x1 = float(x_array_avg[low_lim_idx])
            x2 = float(x_array_avg[high_lim_idx])
            y1 = float(y_array_avg[low_lim_idx])
            y2 = float(y_array_avg[high_lim_idx])
            m = (y2-y1)/(x2-x1)
            y_avg = m*x_val + (y2-m*x2)
        if y_avg == y_val:
            continue
        elif (y_val == 0 and y_avg > 40) or (y_avg/y_val) > 1.33:
            in_time = "%d hours, %d minutes" % (int(x_val//100), int(x_val%100*60/100))
            output.append('<div class="alert text-center alert-success"> <strong>Good!</strong> Usage curbed at <strong>%s</strong> </div>' % in_time) #"Good! Drop at %s   " % in_time
        elif (y_avg/y_val) < 0.67:
            in_time = "%d hours, %d minutes" % (int(x_val//100), int(x_val%100*60/100))
            diff = math.fabs(y_avg-y_val)
            db = pd.read_csv("/home/Oakhack2019/mysite/devices.txt")
            pwr_lst = db["Power"].values.tolist()
            pwr_dupl = [math.fabs(i-diff) for i in pwr_lst]
            suggest_idx = pwr_dupl.index(min(pwr_dupl))
            content_add = "<br><u><strong>Suggestion: </strong> Turn off %s</u>" % db["Name"][suggest_idx]
            try:
                if output[-1][36] == "d":
                    output.append('<div class="alert text-center alert-danger"> <strong>Hey!</strong> Consumption still out of range at <strong>%s</strong> %s </div>' % (in_time,content_add))
                elif output[-1][36] == "w" and output[-2][36] == "w":
                    output.append('<div class="alert text-center alert-danger"> <strong>Hey!</strong> Consumption still out of range at <strong>%s</strong> %s </div>' % (in_time,content_add))
                else:
                    output.append('<div class="alert text-center alert-warning"> <strong>Uh-oh!</strong> Power usage spiked at <strong>%s</strong> %s </div>' % (in_time,content_add))
            except IndexError:
                output.append('<div class="alert text-center alert-warning"> <strong>Uh-oh!</strong> Power usage spiked at <strong>%s</strong> %s </div>' % (in_time,content_add))
    #return str(output)
    #return str(list(reversed(output)))
    output_var = ""
    for out in list(reversed(output)):
        #return str(out)
        output_var += out
    return output_var

def get_chart_regular(x_lim, y_array_r, line_name):
    y_array = [0] + y_array_r
    x_array = range(x_lim+1)
    line_chart = pygal.Line()
    line_chart.x_labels = map(str, x_array)
    line_chart.add(line_name, y_array)
    #chart = line_chart.render_data_uri()
    return line_chart.render_response()

def test_graph(x_array, y_array):
    x = [int(x) for x in x_array.tolist()]
    y = [int(y) for y in y_array.tolist()]
    plt.plot(x, y)
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    plt.title('My first graph!')
    plt.savefig("graph.png")

app = Flask(__name__)
@app.route('/')
def homepage():
    return "Hello from Hell!"

@app.route("/off/<power>/<dev_idx>")
def record_drop(power,dev_idx):
    f = open("/home/Oakhack2019/mysite/data.txt", "r")
    #return "%s" % power
    power = int(power)
    file = f.read()
    last_power_val = int(file.split(",")[-1])
    new_power_val = last_power_val - power
    val = (time.gmtime()[4]+time.gmtime()[3]*60 + 330) % 1440
    time_now = int(round((val // 60 * 100) + (val % 60.0) / 60 * 100))
    #return "YO"
    if int(file.split("\n")[-1].split(",")[0]) == time_now:
        #return "YO"
        #return "YO"
        past_vals = file.split("\n")[:-1]
        write_val = ""
        for val in past_vals:
            write_val += val + "\n"
        write_val += "%d,%d" % (time_now,new_power_val)
        #return "YO"
        w = open("/home/Oakhack2019/mysite/data.txt", "w")
        #return "YO"
        w.write(write_val)
        w.close()
        #return "YO"
    else:
        a = open("/home/Oakhack2019/mysite/data.txt", "a")
        #return "YO"
        a.write("\n%d,%d"%(time_now,new_power_val))
        #return "YO"
    #return "YO"
    dev_db = pd.read_csv("/home/Oakhack2019/mysite/devices.txt")
    #return "YO"
    #return str(dev_db)
    #return str(dev_db["Status"][dev_idx])
    dev_db.at[int(dev_idx), "Status"] = False
    #return "YO"
    #return str(dev_db[dev_idx]["Status"] == False)# = not dev_db[dev_idx]["Status"]
    #return "YO"
    dev_db.to_csv("/home/Oakhack2019/mysite/devices.txt")
    r = open("/home/Oakhack2019/mysite/devices.txt", "r")
    contents_raw = str(r.read())
    contents_done = contents_raw[1:-1]
    w = open("/home/Oakhack2019/mysite/devices.txt", "w")
    w.write(contents_done)
    w.close()
    #return "Sent values %d and %d" % (time_now,new_power_val)
    return '<meta http-equiv="refresh" content="0; URL=http://oakhack2019.pythonanywhere.com/dashboard"> <meta name="keywords" content="automatic redirection">'

@app.route("/on/<power>/<dev_idx>")
def record_spike(power,dev_idx):
    f = open("/home/Oakhack2019/mysite/data.txt", "r")
    #return "%s" % power
    power = int(power)
    file = f.read()
    last_power_val = int(file.split(",")[-1])
    new_power_val = last_power_val + power
    val = (time.gmtime()[4]+time.gmtime()[3]*60 + 330) % 1440
    time_now = int(round((val // 60 * 100) + (val % 60.0) / 60 * 100))
    #return "YO"
    if int(file.split("\n")[-1].split(",")[0]) == time_now:
        #return "YO"
        #return "YO"
        past_vals = file.split("\n")[:-1]
        write_val = ""
        for val in past_vals:
            write_val += val + "\n"
        write_val += "%d,%d" % (time_now,new_power_val)
        #return "YO"
        w = open("/home/Oakhack2019/mysite/data.txt", "w")
        #return "YO"
        w.write(write_val)
        w.close()
        #return "YO"
    else:
        a = open("/home/Oakhack2019/mysite/data.txt", "a")
        #return "YO"
        a.write("\n%d,%d"%(time_now,new_power_val))
        #return "YO"
    #return "YO"
    dev_db = pd.read_csv("/home/Oakhack2019/mysite/devices.txt")
    #return "YO"
    #return str(dev_db)
    #return str(dev_db["Status"][dev_idx])
    dev_db.at[int(dev_idx), "Status"] = True
    #return "YO"
    #return str(dev_db[dev_idx]["Status"] == False)# = not dev_db[dev_idx]["Status"]
    #return "YO"
    dev_db.to_csv("/home/Oakhack2019/mysite/devices.txt")
    r = open("/home/Oakhack2019/mysite/devices.txt", "r")
    contents_raw = str(r.read())
    contents_done = contents_raw[1:-1]
    w = open("/home/Oakhack2019/mysite/devices.txt", "w")
    w.write(contents_done)
    w.close()
    #return "Sent values %d and %d" % (time_now,new_power_val)
    return '<meta http-equiv="refresh" content="0; URL=http://oakhack2019.pythonanywhere.com/dashboard"> <meta name="keywords" content="automatic redirection">'

@app.route("/dashboard")
def render_dash():
    count = 0
    content = ""
    r = open("/home/Oakhack2019/mysite/devices.txt", "r")
    txt = r.read()
    for val in txt.split("\n")[1:]:
        if count == 0:
            content += '<div class="row">'
        lst = val.split(",")
        if lst[5] == 'True':
            button = '<a href="http://oakhack2019.pythonanywhere.com/off/%s/%s" role="button" class="btn btn-primary btn-block">Turn off</a>' % (lst[3], lst[0])
        elif lst[5] == 'False':
            button = '<a href="http://oakhack2019.pythonanywhere.com/on/%s/%s" role="button" class="btn btn-dark btn-block">Turn on</a>' % (lst[3], lst[0])
        content += '<div class="col-md-3"> <div class="card"> <div class="card-body"> <h4 class="text-center">%s<hr></h4> <strong>Location: </strong>%s <br> <strong>Power rating: </strong>%s W <br> <strong>Description: </strong>%s <hr> %s </div> </div> </div>' % (lst[1], lst[2], lst[3], lst[4], button)
        count += 1
        count = count % 4
        if count == 0:
            content += "</div><br>"
    for dummy in range((4-count)%4):
        content += '<div class="col-md-3"> </div>'
    #return render_template("dashboard.html", Username=user, content_app=content)
    read_html = open("/home/Oakhack2019/mysite/templates/dashboard.html", "r")
    #return "YO"
    html_code = read_html.read()
    html_code = html_code.replace("{{Username}}", "User")
    html_code = html_code.replace("{{content_app}}", content)
    db = pd.read_csv("/home/Oakhack2019/mysite/data_avg.txt")
    db_cur = pd.read_csv("/home/Oakhack2019/mysite/data.txt")
    #return "YO"
    msg = comparison(db_cur["time"].values.tolist(),db_cur["power"].values.tolist(),db["time"].values.tolist(),db["power"].values.tolist())
    html_code = html_code.replace("{{notif}}", msg)
    return html_code

@app.route("/graph")
def render_graph():
    #return "YO"
    f = open("/home/Oakhack2019/mysite/data.txt", "r")
    #return "YO"
    file = f.read()
    #return "YO"
    file_final = file.encode("utf-8").decode("utf-8")
    string = StringIO(file_final)
    #return "string: %s" % str(string)
    db = pd.read_csv(string)
    #return "YO"
    x = db["time"].values
    y = db["power"].values

    f2 = open("/home/Oakhack2019/mysite/data_avg.txt", "r")
    #return "YO"
    file2 = f2.read()
    #return "YO"
    file_final2 = file2.encode("utf-8").decode("utf-8")
    string2 = StringIO(file_final2)
    #return "string: %s" % str(string)
    db2 = pd.read_csv(string2)
    #return "YO"
    x2 = db2["time"].values
    y2 = db2["power"].values

    dev_db = pd.read_csv("/home/Oakhack2019/mysite/devices.txt")
    max_capacity = sum(dev_db["Power"].values)
    #return str(max_capacity)

    #return (`x`+`y`)
    #coefs = np.polynomial.polynomial.polyfit(x, y, DEGREE)
    #ffit = np.poly1d(coefs)
    #x_new = np.linspace(x[0], x[-1], num=len(x)*10)

    #coefs = poly.polyfit(x, y, DEGREE)
    #ffit = poly.polyval(x_new, coefs)
    #plt.plot(x_new, ffit)
    #plt.savefig("graph.png")
    #test_graph(x,y)
    plt.plot(x, y, "b-")
    plt.xlabel("Time (hours in a day)")
    plt.ylabel("Power consumption")
    plt.savefig("graph.png")
    plt.plot(x2, y2, "y-")
    plt.axis([0,2400,0,max_capacity])
    plt.savefig("graph_compare.png")
    plt.cla()

    return '<center><img src="https://www.pythonanywhere.com/user/Oakhack2019/files/home/Oakhack2019/graph.png" alt="" style="width:70%;"></center><meta http-equiv="refresh" content="5; URL="http://www.yourdomain.com/yoursite.html">'

@app.route("/post", methods=["POST"])
def add_device():
    result = request.form
    _dict = result.to_dict()
    #return "Name of device: %s\nDescription: %s\nLocation: %s\nPower: %s W" % (_dict["namePost"], _dict["descrPost"], _dict["locPost"], _dict["powerPost"])
    a = open("/home/Oakhack2019/mysite/devices.txt", "a")
    r = open("/home/Oakhack2019/mysite/devices.txt", "r")
    #return "YO"
    contents = r.read()
    a.write("\n")
    line = "%s,%s,%s,%s,%s,False" % (str(len(contents.split("\n"))-1),_dict["namePost"],_dict["locPost"],str(_dict["powerPost"]),_dict["descrPost"])
    a.write(str(line))
    #return line
    return '<meta http-equiv="refresh" content="0; URL=http://oakhack2019.pythonanywhere.com/dashboard"> <meta name="keywords" content="automatic redirection">'

@app.route("/clear")
def turn_all_of():
    r = open("/home/Oakhack2019/mysite/devices.txt", "r")
    red = r.read()
    red_edit = red.replace("True", "False")
    #return "YO"
    w = open("/home/Oakhack2019/mysite/devices.txt", "w")
    val = (time.gmtime()[4]+time.gmtime()[3]*60 + 330) % 1440
    time_now = int(round((val // 60 * 100) + (val % 60.0) / 60 * 100))
    w.write(red_edit)
    w2 = open("/home/Oakhack2019/mysite/data.txt", "a")
    w2.write("\n%d,0" % time_now)
    return '<meta http-equiv="refresh" content="0; URL=http://oakhack2019.pythonanywhere.com/dashboard"> <meta name="keywords" content="automatic redirection">'

@app.route("/test")
def testing():
    db = pd.read_csv("/home/Oakhack2019/mysite/data_avg.txt")
    db_cur = pd.read_csv("/home/Oakhack2019/mysite/data.txt")
    #return "YO"
    msg = comparison(db_cur["time"].values.tolist(),db_cur["power"].values.tolist(),db["time"].values.tolist(),db["power"].values.tolist())
    return msg
