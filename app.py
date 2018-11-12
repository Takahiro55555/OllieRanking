#-*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, url_for
import json, sys, pprint, time, random, hashlib
from datetime import datetime
#sys.path.append("./mymodules")

app = Flask(__name__)


def SaveData(data ,_file_name = 'test'):
    _file_name += '.json'
    with open(_file_name, 'w') as file:
        json.dump(data, file, indent=4)
    print("saved data on " + _file_name)
    return 0
def ReadData(_file_name = 'test'):
    _file_name += '.json'
    with open(_file_name) as file:
        ranking = json.load(file)
    print("read data from " + _file_name)    
    return ranking


# 排他制御!? ナニソレオイシイノ??????
#golobal variables
file_name = "test"
data_push_link = "fff2d2127188a272e7d87f9f5396e7d7"
ranking = ReadData(file_name)


@app.route("/push_data/" + data_push_link, methods=["GET"])
def PushData():
    def ReturnRandomHash(solt = 44124):
        #本来のsoltとは違うかも
        tmp = "hoge{}{}{}".format(random.randint(-10000, 10000), solt, datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        return str(hashlib.md5(tmp.encode()).hexdigest())
    def SortRanking(data):
        data.sort(key=lambda x: x["entry_num"])
        data.reverse()
        data.sort(key=lambda x: x["score"])
        data.reverse()
        return data
    result = {"usr_id": "", "rename_url": "", "time_stamp": "", "name": "", "receved_time_unix": 0, "entry_num": 0, "score": 0,  "name_edited": 0}    
    result["rename_url"] = ReturnRandomHash(437210975)
    result["usr_id"] = ReturnRandomHash(57294375)
    result["score"] = int(request.args.get("score"))
    result["time_stamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    result["name"] = str(request.args.get("name"))
    result["receved_time_unix"] = int(time.mktime(datetime.now().timetuple()))
    result["entry_num"] = len(ranking)
    ranking = ReadData('test')
    ranking.append(result)
    ranking = SortRanking(ranking)
    SaveData(ranking, 'test')
    return render_template("received_msg.html")

@app.route("/show_rename_qr_code")
def ShowRenameQrCode():
    rename_url = "/rename/"

    return render_template("show_rename_qr_code.html", rename_url = rename_url)

@app.route('/rename/<rename_url>')
def rename(rename_url):
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        #return render_template("rename_resutl.html", result_data=result_data)
        return "valid page!!!"
    else:
        #return render_template("rename_error.html")
        return "ERROR!!!"

@app.route('/rename/<rename_url>/result', methods=['GET'])
def rename_result(rename_url):
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        ranking[i]["name"] = str(request.args.get("name"))
        ranking[i]["name_edited"] += 1
        ranking[i]["renamed_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        result_data = ranking[i]
        SaveData(ranking)
        #return render_template("rename_resutl.html", result_data=result_data)
        return "Success!!!"
    else:
        #return render_template("rename_error.html")
        return "ERROR!!!"

@app.route("/")
def TopPage():
    ranking = ReadData('test')
    name = "hoge"
    return render_template("top_page.html", ranking = ranking)


@app.route("/ranking15")
def ShowTopPage():
    ranking = ReadData('test')
    return render_template("ranking15.html", ranking=ranking)

@app.route("/search_rank", methods=['GET'])
@app.route("/ranking15/search_rank", methods=['GET'])
def SearchRank():
    return "serach rank"


if __name__ == '__main__':
    app.run(debug=True)
