#-*- coding: utf-8 -*-
#!/usr/bin/env python3

from flask import Flask, render_template, request, url_for
import json, time, random, hashlib, qrcode
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
file_name = "test2"
data_push_link = "fff2d2127188a272e7d87f9f5396e7d7"
show_rename_qr_code_link = "77da6549b9ab3200490b2ed4d2a502d5"
ranking = ReadData(file_name)
renameble_score = 100
renameble_score_index = 0
qrcode_img_name = "/static/qrcode/qrcode.png"
qrcode_img_path = qrcode_img_name

front_url = "http://35.185.47.65:55555"
rename_url_full = front_url + "/rename"
common_urls = {"top_page": ""}
common_urls["top_page"] = front_url
common_urls["ranking15_page"] = front_url + "/" + "ranking15"
common_urls["search_rank_page"] = front_url + "/" + "search_rank"



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
    ranking = ReadData(file_name)
    result["entry_num"] = len(ranking)
    ranking.append(result)
    ranking = SortRanking(ranking)
    SaveData(ranking, file_name)
    return "receved data"

@app.route("/show_rename_qr_code/" + show_rename_qr_code_link)
def ShowRenameQrCode():
    global ranking, rename_url_full, qrcode_img_name, renameble_score_index, qrcode_img_path
    ranking_len = len(ranking)
    for i in range(ranking_len):
        #一番最後に入ってきたプレイヤー情報のエントリー番号 == ranking配列の長さ
        if ranking[i]["entry_num"] == ranking_len - 1:
            break
    if (ranking[i]["score"] >= renameble_score):
        renameble_score_index = i
        rename_url_full = front_url + "/rename/" + ranking[i]["rename_url"]
        qrcode_img = qrcode.make(rename_url_full)
        qrcode_img.save("." + qrcode_img_name)
        qrcode_img_path = qrcode_img_name + "?" + str(ranking[renameble_score_index]["receved_time_unix"])
    return render_template("show_rename_qr_code.html", rename_url_full = rename_url_full, qrcode_img_path = qrcode_img_path, game_data = ranking[renameble_score_index], rank = renameble_score_index + 1)


@app.route('/rename/<rename_url>')
def rename(rename_url):
    global ranking
    global rename_url_full
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        return render_template("rename.html", data = ranking[i], rename_url_result = rename_url_full + "/result")
    else:
        return render_template("rename_error.html")

@app.route('/rename/<rename_url>/result', methods=['GET'])
def RenameResult(rename_url):
    global ranking, file_name
    print(rename_url)
    for i in range(len(ranking)):
        if ranking[i]["rename_url"] == rename_url:
            break
    if (ranking[i]["rename_url"] == rename_url and ranking[i]["name_edited"] == 0):
        ranking[i]["name"] = str(request.args.get("name"))
        ranking[i]["name_edited"] += 1
        ranking[i]["renamed_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        SaveData(ranking, file_name)
        return render_template("rename_result.html", data = ranking[i], common_urls = common_urls)
    else:
        return render_template("rename_result_error.html", data = ranking[i])

@app.route("/")
def TopPage():
    ranking = ReadData(file_name)
    return render_template("top_page.html", ranking = ranking, common_urls = common_urls)


@app.route("/ranking15")
def Ranking15():
    global ranking, common_urls
    ranking_len = len(ranking)
    if(ranking_len > 15):
        ranking_len = 15
    return render_template("ranking15.html", ranking=ranking, ranking_len = ranking_len, common_urls = common_urls)

@app.route("/search_rank", methods=['GET'])
# @app.route("/ranking15/search_rank", methods=['GET'])
def SearchRank():
    global ranking, common_urls
    serch_result = []
    serch_words = []
    ranking_len = len(ranking)
    serch_words.append(request.args.get("word"))
    print(serch_words)
    for i in range(ranking_len):
        if str(ranking[i]["entry_num"]) == serch_words[0]:
            serch_result.append(ranking[i])
            serch_result[len(serch_result)-1]["rank"] = i + 1
            break
    serch_result_len = len(serch_result)
    if serch_result_len == 0:
        tmp = {"name": "該当なし", "rank": "---", "time_stamp": "---", "renamed_time": "---", "score": "---"}
        serch_result.append(tmp)
        serch_result_len = len(serch_result)
    return render_template("search_rank.html", serch_result = serch_result, common_urls = common_urls, serch_result_len = serch_result_len, )


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False, host='0.0.0.0', port=55555)

