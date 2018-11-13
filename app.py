#-*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for
import json, time, random, hashlib
from datetime import datetime

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
show_rename_qr_code_link = "77da6549b9ab3200490b2ed4d2a502d5"
ranking = ReadData(file_name)
renameble_score = 100

front_url = "http://127.0.0.1:5000"
rename_url_full = front_url + "/rename/"


@app.route("/push_data/" + data_push_link, methods=['GET'])
def PushData():
    global ranking
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
    result["name"] = "無名のスケーター"
    result["receved_time_unix"] = int(time.mktime(datetime.now().timetuple()))
    ranking = ReadData('test')
    result["entry_num"] = len(ranking)
    ranking.append(result)
    ranking = SortRanking(ranking)
    SaveData(ranking, 'test')
    return "receved data"

@app.route("/show_rename_qr_code/" + show_rename_qr_code_link)
def ShowRenameQrCode():
    global ranking
    global  rename_url_full
    ranking_len = len(ranking)
    for i in range(ranking_len):
        #一番最後に入ってきたプレイヤー情報のエントリー番号 == ranking配列の長さ
        if ranking[i]["entry_num"] == ranking_len - 1:
            break    
    if (ranking[i]["score"] >= renameble_score):
        rename_url_full = front_url + "/rename/" + ranking[i]["rename_url"]
    return render_template("show_rename_qr_code.html", rename_url_full = rename_url_full)

@app.route('/rename/<rename_url>')
def rename(rename_url):
    global ranking
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        return render_template("rename.html", data = ranking[i])
    else:
        return render_template("rename_error.html")

@app.route('/rename/<rename_url>/result', methods=['GET'])
def RenameResult(rename_url):
    global ranking
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        ranking[i]["name"] = str(request.args.get("name"))
        ranking[i]["name_edited"] += 1
        ranking[i]["renamed_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        SaveData(ranking)
        return render_template("rename_result.html", data = ranking[i])
    else:
        return render_template("rename_result_error.html", data = ranking[i])

@app.route("/")
def TopPage():
    ranking = ReadData('test')
    return render_template("top_page.html", ranking = ranking)


@app.route("/ranking15")
def Ranking15():
    global ranking
    return render_template("ranking15.html", ranking=ranking)

@app.route("/search_rank", methods=['GET'])
@app.route("/ranking15/search_rank", methods=['GET'])
def SearchRank():
    global ranking
    serch_result = ranking[0]
    return render_template("search_rank.html", serch_result = serch_result)


if __name__ == '__main__':
    app.run(debug=True)
