from flask import Flask, request, abort
from config import DevConfig
from bot_config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, MSSQL_ENGINE, MSSQL_DRIVER, API_KEY

from datetime import datetime

import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from Naked.toolshed.shell import muterun_js

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *



engine = create_engine(MSSQL_ENGINE)
cnxn = pyodbc.connect(MSSQL_DRIVER)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Flask 類別成為 instance
app = Flask(__name__)
app.config.from_object(DevConfig)


@app.route("/CampusChatbot", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return '', 200


@handler.add(MessageEvent, message=TextMessage)
def reply_message(event):
    mtext = check_if_button_click(event.message.text)
    # get intent from mtext in order to return the optimize answer
    intent = mtext.split('/')[0]
    question_feedback_intent = mtext.split('(|)')[0]
    user_question = event.message.text
    # 課程相關
    if intent == '課程種類一覽':
        message = show_course(mtext, user_question)
    elif intent == '免修申請':
        message = course_exemption(mtext, user_question)
    elif intent == '免擋修申請':
        message = no_block_course(mtext, user_question)
    elif intent == '考古題相關':
        message = archaeological_question(mtext, user_question)
    # 系所畢業相關資格規定
    elif intent == '系所畢業資格' or intent == '@系所畢業規定':
        message = graguated_information(mtext)
    elif intent == '@詢問畢業規定':
        message = ask_graguated_information(mtext)
    # 各系所申請入學相關
    elif intent == '各系所申請報名方式':
        message = academy_admission(mtext)
    elif intent == '@系所申請' or intent == '五年碩與逕博規定':
        message = regular_admission(mtext)
    elif intent == '@入學方式':
        message = department_admission(mtext)
    elif intent == '@五年碩申請方式':
        message = five_years_master_degree_admission(mtext)
    elif intent == '@逕博申請方式':
        message = doctor_admission(mtext)
    elif intent == '@輔系與雙主修':
        message = aux_and_double_major_admission(mtext)
    elif intent == '@輔系申請' or intent == '輔修申請':
        message = aux_admission(mtext, user_question)
    elif intent == '@輔系申請規定':
        message = aux_admission_information(mtext)
    elif intent == '@雙主修申請' or intent == '雙主修申請':
        message = double_major_admission(mtext)
    elif intent == '@雙主修申請規定':
        message = double_major_admission_information(mtext, user_question)
    elif intent == '@轉換系所' or intent == '轉換系所':
        message = transfer_department_admission(mtext)
    elif intent == '@轉入系所':
        message = transfer_department_in(mtext)
    elif intent == '@轉出系所':
        message = transfer_department_out(mtext)
    elif intent == '@雙聯學位' or intent == '雙聯學位申請':
        message = double_degree_admission(mtext)
    elif intent == '@雙聯學位申請規定':
        message = double_degree_admission_information(mtext)
    # 獎助學金申請
    elif intent == '獎學金申請':
        message = scholarship(mtext)
    # 學分抵免相關
    elif intent == '修課規定':
        message = course_rule(mtext)
    elif intent == '系所學分抵免規定' or intent == '@系所學分抵免規定':
        message = credits_waiver_and_transference(mtext)
    elif intent == '上修學分認定' or intent == '下修學分認定':
        message = credits_waiver_and_transference(mtext)
    elif intent == '@上修學分認定' or intent == '@下修學分認定':
        message = credits_waiver_and_transference(mtext)
    elif intent == '預修學分抵免' or intent == '學分認定':
        message = credits_waiver_and_transference(mtext)
    elif intent == '@預修學分抵免' or intent == '@學分認定':
        message = credits_waiver_and_transference(mtext)
    elif intent == '@詢問學分抵免規定':
        message = ask_credits_waiver_and_transference(mtext)
    # 各單位簡介
    elif intent == '各單位簡介或功能':
        message = introduction_of_department(mtext)
    elif intent == '@歷史沿革' or intent == '各單位的歷史或沿革':
        message = history_of_department(mtext, user_question)
    elif intent == '@未來出路' or intent == '系所未來出路':
        message = future_of_department(mtext, user_question)
    elif intent == '@指導教授':
        message = professer_of_department(mtext)
    elif intent == '@教授選定' or intent == '如何選定指導教授':
        message = professor_choose(mtext, user_question)
    elif intent == '@教授共指' or intent == '共同指導相關規定':
        message = professor_joint(mtext, user_question)
    elif intent == '@教授更換' or intent == '如何更換指導教授':
        message = professor_change(mtext, user_question)
    elif intent == '推薦信相關' or intent == '@推薦信':
        message = recommendation(mtext, user_question)
    # 各式證明申請
    elif intent == '證明申請':
        message = proof(mtext, user_question)
    elif intent == '@停車證明':
        message = parking_regist(mtext)
    # 校內單位工讀、徵才相關機會
    elif intent == '工讀機會':
        message = job()
    # 圖書館相關規定
    elif intent == '圖書館相關規定' or intent == '@圖書館相關規定':
        message = library(mtext)
    elif intent == '@圖書館借還書':
        message = library_detail_behavior(mtext)
    # 能租借之場地或設備一覽
    elif intent == '能租借之場地或設備一覽' or intent == '@能租借之場地或設備一覽':
        message = place_object_borrow(mtext)
    elif intent == '@租借方式':
        message = how_to_borrow(mtext)
    elif intent == '@場地物品詳細資訊':
        message = place_object_detial(mtext)
    # 地圖
    elif intent == '校區地圖':
        message = campus_map(mtext)
    # 游泳館人數
    elif intent == '健身房人數':
        message = get_gym_crowd(user_question)
    elif intent == '游泳池人數':
        message = get_pool_crowd(user_question)
    # 學生餐廳
    elif intent == '餐廳營業時間' or intent == '@學生餐廳':
        message = restaurant(mtext)
    elif intent == '@詢問學生餐廳':
        message = ask_restaurant(mtext, user_question)
    # 答案回饋
    elif question_feedback_intent == '@答案回饋':
        message = answer_feedback(mtext)
    else:
        message = TextSendMessage('無法回覆')

    line_bot_api.reply_message(event.reply_token, message)


def interview_information(mtext) :
    getAnswer = "SELECT Answer from dbo.interview_information WHERE Question = '\n" + mtext + "';"
    answers = pd.read_sql(getAnswer,cnxn)
    if answers.empty or answers["Answer"][0] == '':
        print("[" + mtext + "]:Can not find answer in interview_information")
        if mtext.find('/') > -1:
            mtext = mtext[:mtext.find('/')]
        getRepair = "SELECT Repair from dbo.repair_table WHERE Intent = '\n" + mtext + "';"
        repair = pd.read_sql(getRepair,cnxn)
        if repair.empty or repair["Repair"][0] == '':
            print("[" + mtext + "]:Can not find answer in repair_table")
            return [
                TextSendMessage(text="小幫手無法辨識【"+ mtext +"】這句話的意思，再麻煩您換句話說說看！\n\n或也可以透過【問題回饋】告知我們！謝謝您！"),
                TemplateSendMessage(
                    alt_text="小幫手無法辨識【"+ mtext +"】這句話的意思",
                    template=ButtonsTemplate(
                        title='問題回饋',
                        text="透過問題回饋告訴小幫手哪裏可以改進",
                        actions=[
                            MessageTemplateAction(
                                label='問題回饋',
                                text='@問題回饋'
                            )
                        ]
                    )
                )
            ]
        else :
            message=repair["Repair"][0]
    else:
        message = answers["Answer"][0]
    return TextSendMessage(message)

def place_object_borrow(mtext):
    if len(mtext.split('/')) < 3:
        return repair_function(mtext.split('/')[0])
    building_name = mtext.split('/')[1]
    if building_name == '沒指定':
        return repair_function(mtext.split('/')[0])
    place_object_name = mtext.split('/')[2]
    if mtext.split('/')[0] == '@能租借之場地或設備一覽':
        campus = mtext.split('/')[3]
        if place_object_name == '沒指定':
            place_object_information = "SELECT 場地或設備名稱, 簡短資訊 from dbo.場地物品租借方式 \
                    WHERE 大樓名稱 LIKE '%" + building_name + "%' AND 校區 LIKE '%" + campus +"%';"
        else:
            place_object_information = "SELECT 場地或設備名稱, 簡短資訊 from dbo.場地物品租借方式 \
                    WHERE 大樓名稱 LIKE '%" + building_name + "%' AND 校區 LIKE \
                    '%" + campus +"%'AND 場地或設備名稱 LIKE '%" + place_object_name + "%';"
    else:
        if building_name == '圖書館' or building_name == '活動中心':
            return TemplateSendMessage(
                alt_text='哪個校區的' + building_name + '呢？',
                template=ButtonsTemplate(
                    title=building_name + '場地租借規定',
                    text='請選擇校區',
                    actions=[
                        MessageTemplateAction(
                            label='交大校區',
                            text='@能租借之場地或設備一覽/' + building_name + '/' + place_object_name + '/交大校區'
                        ),
                        MessageTemplateAction(
                            label='陽明校區',
                            text='@能租借之場地或設備一覽/' + building_name + '/' + place_object_name + '/陽明校區'
                        )
                    ]
                )
            )
        if place_object_name == '沒指定':
            place_object_information = "SELECT 場地或設備名稱, 簡短資訊 from dbo.場地物品租借方式 \
                    WHERE 大樓名稱 LIKE '" + building_name + "';"
        else:
            place_object_information = "SELECT 場地或設備名稱, 簡短資訊 from dbo.場地物品租借方式 \
                    WHERE 大樓名稱 LIKE '" + building_name + "' AND 場地或設備名稱 LIKE \
                    '%" + place_object_name + "%';"
    result = pd.read_sql(place_object_information, cnxn)

    place_object_name = result['場地或設備名稱']
    brief = result['簡短資訊']

    if brief.size == 0:
        if mtext.split('/')[2] == '沒指定':
            return TextSendMessage(building_name + '並沒有任何場地或物品可以外借喔！')
        return TextSendMessage(building_name + '並沒有' + mtext.split('/')[2] + '可以外借喔！')
    else:
        if mtext.split('/')[2] == '沒指定':
            rmtext = building_name + '可外借的場地及物品如下: '
        else:
            rmtext = building_name + '可外借的' + mtext.split('/')[2] + \
                '有:'

        place_object_information = []

        item_range = brief.size
        if item_range > 10:
            item_range = 10
        for i in range(item_range):
            brief_text = brief[i]
            if len(brief_text) > 60:
                brief_text = brief_text[:55] + '...'
            place_object_information.append(
                CarouselColumn(
                    title=place_object_name[i],
                    text=brief_text,
                    actions=[
                        MessageTemplateAction(
                            label='借用方式',
                            text='@租借方式/' + building_name + '/' + place_object_name[i]
                        ),
                        MessageTemplateAction(
                            label='詳細資訊',
                            text='@場地物品詳細資訊/' + building_name + '/' + place_object_name[i],
                        )
                    ]
                )
            )

        Carousel_template = TemplateSendMessage(
            alt_text=rmtext,
            template=CarouselTemplate(
                columns=place_object_information
            )
        )
        return [
            TextSendMessage(rmtext),
            Carousel_template
        ]

def how_to_borrow(mtext):
    building_name = mtext.split('/')[1]
    place_object_name = mtext.split('/')[2]
    borrow_way = "SELECT 租借方式 from dbo.場地物品租借方式 \
            WHERE 大樓名稱 = '" + building_name + "' AND 場地或設備名稱 = \
            '" + place_object_name + "';"
    result = pd.read_sql(borrow_way, cnxn)
    message = result['租借方式'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )

    return [
        TextSendMessage(message),
        feedback
    ]


def place_object_detial(mtext):
    building_name = mtext.split('/')[1]
    place_object_name = mtext.split('/')[2]
    borrow_way = "SELECT 詳細資訊 from dbo.場地物品租借方式 \
            WHERE 大樓名稱 = '" + building_name + "' AND 場地或設備名稱 = \
            '" + place_object_name + "';"
    result = pd.read_sql(borrow_way, cnxn)
    message = result['詳細資訊'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def library(mtext):
    if len(mtext.split('/'))<3:
        behavior = mtext.split('/')[1]
        return TemplateSendMessage(
            alt_text='圖書館相關規定',
            template=ButtonsTemplate(
                title='圖書館相關規定',
                text='請選擇校區',
                actions=[
                    MessageTemplateAction(
                        label='交大校區',
                        text='@圖書館相關規定/交大校區/' + behavior
                    ),
                    MessageTemplateAction(
                        label='陽明校區',
                        text='@圖書館相關規定/陽明校區/' + behavior
                    )
                ]
            )
        )
    campus = mtext.split('/')[1]
    behavior = mtext.split('/')[2]
    if behavior == '沒指定':
        return TemplateSendMessage(
            alt_text=campus + '圖書館',
            template=ButtonsTemplate(
            title=campus + '圖書館',
                text='請選擇想知道的規定',
                actions=[
                    MessageTemplateAction(
                        label='借書相關',
                        text='@圖書館相關規定/' + campus + '/借書'
                    ),
                    MessageTemplateAction(
                        label='還書相關',
                        text='@圖書館相關規定/' + campus + '/還書'
                    ),
                    MessageTemplateAction(
                        label='場地租借規定',
                        text='@能租借之場地或設備一覽/圖書館/沒指定/' + campus
                    )
                ]
            )
        )
    behavior_detail = "SELECT 行為細項 from dbo.圖書館借還書 \
            WHERE 校區 LIKE '%" + campus + "%' AND 行為 LIKE \
            '%" + behavior + "%';"
    result = pd.read_sql(behavior_detail, cnxn)
    behavior_detail = []
    for i in range(result.size):
        behavior_detail.append(
            MessageTemplateAction(
                label=result['行為細項'][i],
                text='@圖書館借還書/' + campus + '/' + result['行為細項'][i]
            )
        )
    message = TemplateSendMessage(
        alt_text=campus + '圖書館' + behavior,
        template=ButtonsTemplate(
            title=campus + '圖書館' + behavior,
            text='請選擇想知道的規定',
            actions=behavior_detail
        )
    )
    return message



def library_detail_behavior(mtext):
    campus = mtext.split('/')[1]
    behavior = mtext.split('/')[2]
    behavior_method = "SELECT 方式 from dbo.圖書館借還書 \
        WHERE 校區 LIKE '%" + campus + "%' AND 行為細項 LIKE \
        '%" + behavior + "%';"
    message = pd.read_sql(behavior_method, cnxn)['方式'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def job():
    import urllib.request as req
    url = 'https://infonews.nycu.edu.tw/index.php?SuperType=2&action=more&categoryid=5'

    # create a Request object with Request Header
    request=req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })

    with req.urlopen(request) as response:
        data = response.read().decode('big5')

    # analysis html code
    import bs4
    root = bs4.BeautifulSoup(data, "html.parser")
    jobs = root.find_all("td", rowspan=1, class_="style2")
    date_emplyer = root.find_all("td", rowspan=1, class_="style4")
    job_context = []

    job_count = 0
    date_emplyer_count = 0
    while job_count < 5:
        job_name = jobs[job_count].a.string
        if len(job_name) > 35:
            job_name = job_name[:35] + '...'

        if jobs[job_count].a is not None:
            job_context.append(
                CarouselColumn(
                    title=job_name,
                    text='招募日期：' + date_emplyer[date_emplyer_count].string + '\n招募單位：' + date_emplyer[date_emplyer_count+1].string.split(']')[0] + ']',
                    actions=[
                        URITemplateAction(
                            label='詳細內容',
                            uri='https://infonews.nycu.edu.tw/' + jobs[job_count].a['href']
                        )
                    ]
                )
            )
            job_count += 1
            date_emplyer_count += 2

    job_context.append(
        CarouselColumn(
            title='更多工讀資訊',
            text='請洽校內徵才公告',
            actions=[
                URITemplateAction(
                    label='校內徵才公告',
                    uri=url
                )
            ]
        )
    )

    message = TemplateSendMessage(
        alt_text='從校內徵才公告找到的內容如下：',
        template=CarouselTemplate(
            columns=job_context
        )
    )


    return message


def proof(mtext, user_question):
    if len(mtext.split('/')) != 2:
        return repair_function(mtext.split('/')[0])
    elif mtext.split('/')[1] == '停車證':
        return TemplateSendMessage(
            alt_text='請選擇您的身份',
            template=ButtonsTemplate(
                title='停車證種類',
                text='請選擇您的身份',
                actions=[
                    MessageTemplateAction(
                        label='教職員工',
                        text='@停車證明/教職員工'
                    ),MessageTemplateAction(
                        label='學生',
                        text='@停車證明/學生'
                    ),MessageTemplateAction(
                        label='校友',
                        text='@停車證明/校友'
                    ),MessageTemplateAction(
                        label='外校人士',
                        text='@停車證明/外校人士'
                    )
                ]
            )
        )
    elif mtext.split('/')[1] == '在學證明':
        result = pd.read_sql("SELECT Answer from dbo.interview_information \
                WHERE Question LIKE '%" + mtext + "%'", cnxn)
        return TextSendMessage(text=result['Answer'][0])
    else:
        return repair_function(mtext.split('/')[0])


def parking_regist(mtext):
    import urllib.request as req
    url = 'https://www.ga.nctu.edu.tw/security-division/parking'

    # create a Request object with Request Header
    request=req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })

    with req.urlopen(request) as response:
        data = response.read().decode('utf-8')

    import bs4
    root = bs4.BeautifulSoup(data, "html.parser")
    parking = root.find_all("div", class_="page links")
    # print(parking[0])
    parking_registers = parking[0].find_all("li", class_="list-group-item")
    import re
    identity_count = 0
    staffs = []
    students = []
    alumni = []
    external_users = []
    for parking_register in parking_registers:
        if identity_count < 3:
            staffs.append({
                'title': re.split('[A-Z]', parking_register.a.text)[0],
                'link': parking_register.a['href']
            })
        elif 3 <= identity_count < 7:
            students.append({
                'title': re.split('[A-Z]', parking_register.a.text)[0],
                'link': parking_register.a['href']
            })
        elif 7 <= identity_count < 9:
            alumni.append({
                'title': re.split('[A-Z]', parking_register.a.text)[0],
                'link': parking_register.a['href']
            })
        else:
            external_users.append({
                'title': re.split('[A-Z]', parking_register.a.text)[0],
                'link': parking_register.a['href']
            })

        identity_count += 1

    send = []
    if mtext.split('/')[1] == '教職員工':
        for staff in staffs:
            send.append(
                URITemplateAction(
                    label=staff['title'],
                    uri=staff['link']
                )
            )
    elif mtext.split('/')[1] == '學生':
        for student in students:
            send.append(
                URITemplateAction(
                    label=student['title'],
                    uri=student['link']
                )
            )
    elif mtext.split('/')[1] == '校友':
        for alumna in alumni:
            send.append(
                URITemplateAction(
                    label=alumna['title'],
                    uri=alumna['link']
                )
            )
    else:
        for external_user in external_users:
            send.append(
                URITemplateAction(
                    label=external_user['title'],
                    uri=external_user['link']
                )
            )

    message = TemplateSendMessage(
        alt_text='請選擇您的欲申請的停車證種類',
        template=ButtonsTemplate(
            title=mtext.split('/')[1] + '停車證申請',
            text='請選擇您的欲申請的停車證種類',
            actions=send
        )
    )

    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        message,
        feedback
    ]

def introduction_of_department(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]

    if education == '大學部':
        education = '沒指定'

    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的介紹資訊呢？',
                    template=ButtonsTemplate(
                        title=department + '的簡介資訊？',
                        text='請問是' + department + '的碩士班還是博士班的介紹資訊呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@各單位簡介或功能/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@各單位簡介或功能/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的介紹嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@各單位簡介或功能/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    if education != '沒指定':
        if group != '沒指定':
            result = pd.read_sql("SELECT 介紹類別 from dbo.各單位簡介或功能 \
                    WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND (學歷 LIKE\
                    '%沒指定%' OR 學歷 LIKE '%" + education + "%') AND (組別 LIKE \
                    '%沒指定%' OR 組別 LIKE '%" + group + "%');", cnxn)
        else:
            result = pd.read_sql("SELECT 介紹類別 from dbo.各單位簡介或功能 \
                    WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND (學歷 LIKE\
                    '%沒指定%' OR 學歷 LIKE '%" + education + "%') AND 組別 LIKE \
                    '%沒指定%';", cnxn)
    else:
        if group != '沒指定':
            result = pd.read_sql("SELECT 介紹類別 from dbo.各單位簡介或功能 \
                    WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND 學歷 LIKE '%沒指定%'\
                    AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')", cnxn)
        else:
            result = pd.read_sql("SELECT 介紹類別 from dbo.各單位簡介或功能 \
                    WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND 學歷 LIKE\
                    '%沒指定%' AND 組別 LIKE '%沒指定%';", cnxn)

    asked_organ = ''
    if academy != '沒指定':
        asked_organ = asked_organ + academy
    if department != '沒指定':
        asked_organ = asked_organ + department
    if education != '沒指定':
        asked_organ = asked_organ + education
    if group != '沒指定':
        asked_organ = asked_organ + group

    if len(result['介紹類別']) == 0:
        return TextSendMessage('並沒有關於' + asked_organ + '的介紹相關資訊喔！或是可能再把系所名稱再清楚一些講出來！')

    rmtext = '請問要詢問' + asked_organ + '的什麼問題呢？'

    return TemplateSendMessage(
        alt_text=rmtext,
        template=ButtonsTemplate(
            title=asked_organ + '簡介',
            text=rmtext,
            actions=[
                MessageTemplateAction(
                    label='歷史沿革',
                    text='@歷史沿革/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                ),MessageTemplateAction(
                    label='未來出路',
                    text='@未來出路/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                ),MessageTemplateAction(
                    label='指導教授相關規定',
                    text='@指導教授/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                ),MessageTemplateAction(
                    label='推薦信',
                    text='@推薦信/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                )
            ]
        )
    )


def history_of_department(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]
    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的歷史沿革呢？',
                    template=ButtonsTemplate(
                        title=department + '的歷史沿革？',
                        text='請問是' + department + '的碩士班還是博士班的歷史沿革呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@歷史沿革/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@歷史沿革/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的歷史沿革嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@歷史沿革/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '歷史沿革';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def future_of_department(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]
    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])
    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的未來出路呢？',
                    template=ButtonsTemplate(
                        title=department + '的未來出路？',
                        text='請問是' + department + '的碩士班還是博士班的未來出路呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@未來出路/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@未來出路/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的未來出路嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@未來出路/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '未來出路';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def professer_of_department(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]
    message = campus + '/' + academy + '/' + department + '/' + education + '/' + group
    return TemplateSendMessage(
        alt_text=department + '指導教授相關規定',
        template=ButtonsTemplate(
            title=department + '指導教授相關規定',
            text='請選擇想知道的規定',
            actions=[
                MessageTemplateAction(
                    label='如何選定指導教授',
                    text='@教授選定/' + message
                ),MessageTemplateAction(
                    label='教授共同指導規定',
                    text='@教授共指/' + message
                ),MessageTemplateAction(
                    label='如何更換指導教授',
                    text='@教授更換/' + message
                )
            ]
        )
    )


def professor_choose(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]

    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的教授選定呢？',
                    template=ButtonsTemplate(
                        title=department + '的教授選定？',
                        text='請問是' + department + '的碩士班還是博士班的教授選定呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@教授選定/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@教授選定/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的教授選定嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@教授選定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '選定指導教授';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def professor_joint(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]

    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])
    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的教授共指規定呢？',
                    template=ButtonsTemplate(
                        title=department + '的教授共指規定？',
                        text='請問是' + department + '的碩士班還是博士班的教授共指規定呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@教授共指/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@教授共指/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的教授共指規定嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@教授共指/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '指導教授共指';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def professor_change(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]

    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的教授更換規定呢？',
                    template=ButtonsTemplate(
                        title=department + '的教授更換規定？',
                        text='請問是' + department + '的碩士班還是博士班的教授更換規定呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@教授更換/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@教授更換/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的教授更換規定嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@教授更換/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '更換指導教授';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def recommendation(mtext, user_question):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]

    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education == '沒指定':
        if department == '沒指定':
            return repair_function(mtext.split('/')[0])
        result = pd.read_sql("SELECT 學歷 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%';", cnxn)

        for edu in result['學歷']:
            if edu != '沒指定' and department != '沒指定':
                return TemplateSendMessage(
                    alt_text='請問是' + department + '的碩士班還是博士班的推薦信呢？',
                    template=ButtonsTemplate(
                        title=department + '的推薦信？',
                        text='請問是' + department + '的碩士班還是博士班的推薦信呢？',
                        actions=[
                            MessageTemplateAction(
                                label='碩士班',
                                text='@推薦信/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                            ),MessageTemplateAction(
                                label='博士班',
                                text='@推薦信/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                            )
                        ]
                    )
                )

    if group == '沒指定':
        result = pd.read_sql("SELECT 組別 from dbo.各單位簡介或功能 \
                WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                '%" + education + "%');", cnxn)

        gp_choice = []
        for gp in result['組別']:
            if gp != '沒指定':
                append_col = CarouselColumn(
                    title=gp,
                    text='想詢問' + gp + '的推薦信嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + gp,
                            text='@推薦信/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                        )
                    ]
                )
                if len(gp_choice) == 0:
                    gp_choice.append(append_col)
                elif append_col not in gp_choice:
                    gp_choice.append(append_col)

        if len(gp_choice) > 0 and len(gp_choice) < 11:
            rmtext = '請問是什麼組別呢？'
            Carousel_template = TemplateSendMessage(
                alt_text=rmtext,
                template=CarouselTemplate(
                    columns=gp_choice
                )
            )

            return [
                TextSendMessage(rmtext),
                Carousel_template
            ]
        # Never Reach Here
        elif len(gp_choice) > 11:
            return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

    result = pd.read_sql("SELECT 介紹內容 from dbo.各單位簡介或功能 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 介紹類別 = '推薦信';", cnxn)
    message = result['介紹內容'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]

def course_rule(mtext):
    if len(mtext.split('/')) < 6:
        return repair_function(mtext.split('/')[0])
    else:
        intent = mtext.split('/')[0]
        campus = mtext.split('/')[1]
        academy = mtext.split('/')[2]
        department = mtext.split('/')[3]
        education = mtext.split('/')[4]
        group = mtext.split('/')[5]

        asked_organ = ''
        if academy != '沒指定':
            asked_organ = asked_organ + academy
        if department != '沒指定':
            asked_organ = asked_organ + department
        if education != '沒指定':
            asked_organ = asked_organ + education
        if group != '沒指定':
            asked_organ = asked_organ + group

        if asked_organ == '':
            return repair_function(mtext.split('/')[0])

        return TemplateSendMessage(
            alt_text='請問是' + asked_organ + '的哪方面的修課資訊呢？',
            template=ButtonsTemplate(
                title=asked_organ + '的修課資訊',
                text='請問是' + asked_organ + '的哪方面的修課資訊呢？',
                actions=[
                    MessageTemplateAction(
                        label='課程學分認定',
                        text='@學分認定/' + campus + '/' + academy + '/' + department + '/' +  education + '/' +  group
                    ),MessageTemplateAction(
                        label='學分抵免規定',
                        text='@系所學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                    ),MessageTemplateAction(
                        label='畢業相關規定',
                        text='@系所畢業規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group
                    )
                ]
            )
        )


def credits_waiver_and_transference(mtext):
    if len(mtext.split('/')) < 6:
        return repair_function(mtext.split('/')[0])
    else:
        intent = mtext.split('/')[0]
        if intent[0] == '@':
            intent = intent.split('@')[1]
        campus = mtext.split('/')[1]
        academy = mtext.split('/')[2]
        department = mtext.split('/')[3]
        education = mtext.split('/')[4]
        group = mtext.split('/')[5]

        if education == '大學部':
            education = '沒指定'

        if education == '沒指定' or education == '':
            if department == '沒指定' or department == '':
                return repair_function(mtext.split('/')[0])
            result = pd.read_sql("SELECT 學歷 from dbo.學分抵免與認定之規定 \
                    WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                    '%" + department + "%';", cnxn)

            for edu in result['學歷']:
                if edu != '沒指定' and department != '沒指定':
                    return TemplateSendMessage(
                        alt_text='請問是' + department + '的碩士班還是博士班的學分資訊呢？',
                        template=ButtonsTemplate(
                            title=department + '的學分資訊？',
                            text='請問是' + department + '的碩士班還是博士班的學分資訊呢？',
                            actions=[
                                MessageTemplateAction(
                                    label='碩士班',
                                    text='@' + intent + '/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                                ),MessageTemplateAction(
                                    label='博士班',
                                    text='@' + intent + '/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                                )
                            ]
                        )
                    )

        if group == '沒指定':
            result = pd.read_sql("SELECT 組別 from dbo.學分抵免與認定之規定 \
                    WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                    '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                    '%" + education + "%');", cnxn)

            gp_choice = []
            for gp in result['組別']:
                if gp != '沒指定':
                    append_col = CarouselColumn(
                        title=gp,
                        text='想詢問' + gp + '的學分資訊嗎？',
                        actions=[
                            MessageTemplateAction(
                                label='詢問' + gp,
                                text='@' + intent + '/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                            )
                        ]
                    )
                    if len(gp_choice) == 0:
                        gp_choice.append(append_col)
                    elif append_col not in gp_choice:
                        gp_choice.append(append_col)

            if len(gp_choice) > 0 and len(gp_choice) < 11:
                rmtext = '請問是什麼組別呢？'
                Carousel_template = TemplateSendMessage(
                    alt_text=rmtext,
                    template=CarouselTemplate(
                        columns=gp_choice
                    )
                )

                return [
                    TextSendMessage(rmtext),
                    Carousel_template
                ]
            # Never Reach Here
            elif len(gp_choice) > 11:
                return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

        if education != '沒指定':
            if group != '沒指定':
                result = pd.read_sql("SELECT 學分問題類別 from dbo.學分抵免與認定之規定 \
                        WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND (學歷 LIKE\
                        '%沒指定%' OR 學歷 LIKE '%" + education + "%') AND (組別 LIKE \
                        '%沒指定%' OR 組別 LIKE '%" + group + "%');", cnxn)
            else:
                result = pd.read_sql("SELECT 學分問題類別 from dbo.學分抵免與認定之規定 \
                        WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND (學歷 LIKE\
                        '%沒指定%' OR 學歷 LIKE '%" + education + "%') AND 組別 LIKE \
                        '%沒指定%';", cnxn)
        else:
            if group != '沒指定':
                result = pd.read_sql("SELECT 學分問題類別 from dbo.學分抵免與認定之規定 \
                        WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND 學歷 LIKE '%沒指定%'\
                        AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')", cnxn)
            else:
                result = pd.read_sql("SELECT 學分問題類別 from dbo.學分抵免與認定之規定 \
                        WHERE 學院 = '" + academy + "' AND 系所 LIKE '%" + department + "%' AND 學歷 LIKE\
                        '%沒指定%' AND 組別 LIKE '%沒指定%';", cnxn)

        asked_organ = ''
        if academy != '沒指定':
            asked_organ = asked_organ + academy
        if department != '沒指定':
            asked_organ = asked_organ + department
        if education != '沒指定':
            asked_organ = asked_organ + education
        if group != '沒指定':
            asked_organ = asked_organ + group

        question_type = []
        if intent == '系所學分抵免規定' or intent == '@系所學分抵免規定':
            for q_type in result['學分問題類別']:
                if '抵免' in q_type:
                    question_type.append(CarouselColumn(
                        title=q_type,
                        text='想詢問' + asked_organ + '的' + q_type + '嗎？',
                        actions=[
                            MessageTemplateAction(
                                label='詢問' + q_type,
                                text='@詢問學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group + '/' + q_type
                            )
                        ]
                    ))
        else:
            for q_type in result['學分問題類別']:
                if intent in q_type:
                    question_type.append(CarouselColumn(
                        title=q_type,
                        text='想詢問' + asked_organ + '的' + q_type + '嗎？',
                        actions=[
                            MessageTemplateAction(
                                label='詢問' + q_type,
                                text='@詢問學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group + '/' + q_type
                            )
                        ]
                    ))

    if len(question_type) == 0:
        return TextSendMessage('並沒有關於' + asked_organ + '的' + intent + '相關資訊喔！或是可能再把系所名稱再清楚一些講出來！')
    elif len(question_type) > 10:
        return TextSendMessage('小幫手發現你想問的' + asked_organ + '的' + intent + '相關資訊有' + len(question_type) + '筆，再麻煩您確定遺下有沒有打錯系所名稱了。')

    rmtext = '請問要詢問' + asked_organ + '的什麼問題呢？'
    Carousel_template = TemplateSendMessage(
        alt_text=rmtext,
        template=CarouselTemplate(
            columns=question_type
        )
    )

    return [
        TextSendMessage(rmtext),
        Carousel_template
    ]


def ask_credits_waiver_and_transference(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]
    question_type = mtext.split('/')[6]

    result = pd.read_sql("SELECT 學分規定 from dbo.學分抵免與認定之規定 \
            WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
             '%" + department + "%' AND (學歷 LIKE '%" + education + "%' OR\
             學歷 LIKE '%沒指定%') AND (組別 LIKE '%" + group + "%' OR 組別 LIKE \
             '%沒指定%') AND 學分問題類別 = '" + question_type + "';", cnxn)

    message = result['學分規定'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def scholarship(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]

    send = []
    send_fix_text = ''

    scholarship_from_nycu = pd.read_sql("SELECT 申請方式 from dbo.獎助學金申請方式 \
            WHERE 種類 LIKE '%獎學金%' AND 學院 LIKE '%沒指定%' AND 系所 LIKE '%沒指定%';", cnxn)

    scholarship_from_nctu = scholarship_from_nycu['申請方式'][0]
    scholarship_from_nymu = scholarship_from_nycu['申請方式'][1]
    if academy != '沒指定' and academy != '':
        scholarship_from_academy = pd.read_sql("SELECT 申請方式 from \
                dbo.獎助學金申請方式 WHERE 種類 LIKE '%獎學金%' AND 學院 LIKE \
                '%" + academy + "%' AND 系所 LIKE '%沒指定%';", cnxn)
        if scholarship_from_academy['申請方式'][0] == '':
            scholarship_from_academy['申請方式'][0] = 'https://test.com'
        send.append(
            URITemplateAction(
                label=academy + '獎學金',
                uri=scholarship_from_academy['申請方式'][0]
            )
        )
        if department != '沒指定' and department != '':
            scholarship_from_department = pd.read_sql("SELECT 申請方式 from \
                    dbo.獎助學金申請方式 WHERE 種類 LIKE '%獎學金%' AND 學院 LIKE \
                    '%" + academy + "%' AND 系所 LIKE '%" + department + "%';", cnxn)
            if scholarship_from_department['申請方式'][0] == '':
                scholarship_from_department['申請方式'][0] = 'https://test.com'
            send.append(
                URITemplateAction(
                    label=department + '獎學金',
                    uri=scholarship_from_department['申請方式'][0]
                )
            )
    else:
        send_fix_text += '小幫手無法判斷你想詢問哪個系所的講學金，若想查詢特定系所的講\
            學金資訊的話，可嘗試換句話說或把系所名稱講得更明確一些！\n\n其他可參考：\n\n'

    send_fix_text += '生輔組獎學金申請流程\n<https://sasystem.nctu.edu.tw/scholarship/doc/step1.pdf>'

    if scholarship_from_nctu == '':
        scholarship_from_nctu = 'https://test.com'
    send.append(
        URITemplateAction(
            label='交大校區獎學金',
            uri=scholarship_from_nctu
        )
    )
    if scholarship_from_nymu == '':
        scholarship_from_nymu = 'https://test.com'
    send.append(
        URITemplateAction(
            label='陽明校區獎學金',
            uri=scholarship_from_nymu
        )
    )

    return [
        TextSendMessage(text=send_fix_text),
        TemplateSendMessage(
            alt_text='以下是能夠申請的獎學金申請',
            template=ButtonsTemplate(
                title='獎學金申請',
                text='以下是能夠申請的獎學金申請',
                actions=send
            )
        )
    ]


def academy_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    show_department = department

    if department == '沒指定':
        if academy == '沒指定':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])
            else:
                show_department = academy + education

    message = campus + '/' + academy + '/' + department + '/' + education

    return TemplateSendMessage(
        alt_text=show_department + '各式學籍相關規定',
        template=ButtonsTemplate(
            title=show_department + '各式學籍相關規定',
            text='請選擇想知道的規定',
            actions=[
                MessageTemplateAction(
                    label='一般系所申請',
                    text='@系所申請/' + message
                ),MessageTemplateAction(
                    label='輔修與雙主修申請',
                    text='@輔系與雙主修/' + message
                ),MessageTemplateAction(
                    label='轉換系所申請',
                    text='@轉換系所/' + message
                ),MessageTemplateAction(
                    label='雙聯學位申請',
                    text='@雙聯學位/' + message
                )
            ]
        )
    )


def double_degree_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    asked_organ = ''
    if academy != '沒指定':
        asked_organ = asked_organ + academy
    if department != '沒指定':
        asked_organ = asked_organ + department
    if education != '沒指定':
        asked_organ = asked_organ + education

    reply = []

    reply.append(CarouselColumn(
        title='雙聯學位申請規定',
        text='想詢問' + asked_organ + '的雙聯學位申請規定嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問申請規定',
                text='@雙聯學位申請規定/' + campus + '/' + academy + '/' + department + '/' + education
            )
        ]
    ))

    reply.append(CarouselColumn(
        title='雙聯學位學分認定',
        text='想詢問' + asked_organ + '的雙聯學位學分認定方式嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問學分認定方式',
                text='@詢問學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/沒指定/雙聯學位學分認定'
            )
        ]
    ))

    return TemplateSendMessage(
        alt_text=asked_organ + '雙聯學位',
        template=CarouselTemplate(
            columns=reply
        )
    )

def double_degree_admission_information(mtext):

    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 雙聯學位申請 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['雙聯學位申請'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def regular_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    show_department = department

    if department == '沒指定':
        show_department = academy + education

    message = campus + '/' + academy + '/' + department + '/' + education

    return TemplateSendMessage(
        alt_text=show_department + '一般入學申請',
        template=ButtonsTemplate(
            title=show_department + '一般入學申請',
            text='請選擇想知道的規定',
            actions=[
                MessageTemplateAction(
                    label='入學方式',
                    text='@入學方式/' + message
                ),MessageTemplateAction(
                    label='五年碩申請方式',
                    text='@五年碩申請方式/' + message
                ),MessageTemplateAction(
                    label='逕博申請方式',
                    text='@逕博申請方式/' + message
                )
            ]
        )
    )


def aux_and_double_major_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    show_department = department

    if department == '沒指定':
        show_department = academy + education

    message = campus + '/' + academy + '/' + department + '/' + education

    return TemplateSendMessage(
        alt_text=show_department + '輔系與雙主修申請',
        template=ButtonsTemplate(
            title='輔系與雙主修申請',
            text='請選擇想知道的規定',
            actions=[
                MessageTemplateAction(
                    label=show_department + '輔系申請方式',
                    text='@輔系申請/' + message
                ),MessageTemplateAction(
                    label=show_department + '雙主修申請方式',
                    text='@雙主修申請/' + message
                )
            ]
        )
    )


def aux_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if department == '沒指定':
        if academy == '沒指定':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education != '碩士在職專班':
        education = '沒指定'

    asked_organ = ''
    if academy != '沒指定':
        asked_organ = asked_organ + academy
    if department != '沒指定':
        asked_organ = asked_organ + department
    if education != '沒指定':
        asked_organ = asked_organ + education

    reply = []

    reply.append(CarouselColumn(
        title='輔系申請規定',
        text='想詢問' + asked_organ + '的輔系申請規定嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問申請規定',
                text='@輔系申請規定/' + campus + '/' + academy + '/' + department + '/' + education
            )
        ]
    ))

    reply.append(CarouselColumn(
        title='輔系學分認定',
        text='想詢問' + asked_organ + '的輔系學分認定方式嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問學分認定方式',
                text='@詢問學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/沒指定/雙主修與輔系學分認定'
            )
        ]
    ))

    return TemplateSendMessage(
        alt_text=asked_organ + '輔系',
        template=CarouselTemplate(
            columns=reply
        )
    )


def aux_admission_information(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if department == '沒指定':
        if academy == '沒指定':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 輔系申請 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['輔系申請'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def double_major_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if department == '沒指定':
        if academy == '沒指定':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education != '碩士在職專班':
        education = '沒指定'

    asked_organ = ''
    if academy != '沒指定':
        asked_organ = asked_organ + academy
    if department != '沒指定':
        asked_organ = asked_organ + department
    if education != '沒指定':
        asked_organ = asked_organ + education

    reply = []

    reply.append(CarouselColumn(
        title='雙主修申請規定',
        text='想詢問' + asked_organ + '的雙主修申請規定嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問申請規定',
                text='@雙主修申請規定/' + campus + '/' + academy + '/' + department + '/' + education
            )
        ]
    ))

    reply.append(CarouselColumn(
        title='雙主修學分認定',
        text='想詢問' + asked_organ + '的雙主修學分認定方式嗎？',
        actions=[
            MessageTemplateAction(
                label='詢問學分認定方式',
                text='@詢問學分抵免規定/' + campus + '/' + academy + '/' + department + '/' + education + '/沒指定/雙主修與輔系學分認定'
            )
        ]
    ))

    return TemplateSendMessage(
        alt_text=asked_organ + '雙主修',
        template=CarouselTemplate(
            columns=reply
        )
    )


def double_major_admission_information(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if department == '沒指定':
        if academy == '沒指定':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 雙主修申請 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['雙主修申請'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]

def transfer_department_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    show_department = department

    if department == '沒指定' or department == '':
        if academy == '沒指定' or academy == '':
            return repair_function(mtext.split('/')[0])
        else:
            if education != '碩士在職專班':
                return repair_function(mtext.split('/')[0])
            else:
                show_department = academy + education

    message = campus + '/' + academy + '/' + department + '/' + education

    return TemplateSendMessage(
        alt_text=show_department + '轉系相關規定',
        template=ButtonsTemplate(
            title=show_department + '轉系相關規定',
            text='請選擇想知道的規定',
            actions=[
                MessageTemplateAction(
                    label='轉入' + show_department,
                    text='@轉入系所/' + message
                ),MessageTemplateAction(
                    label='轉出' + show_department,
                    text='@轉出系所/' + message
                )
            ]
        )
    )


def transfer_department_in(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 轉入系所 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['轉入系所'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def transfer_department_out(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 轉出系所 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['轉出系所'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def department_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 入學方式 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['入學方式'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def five_years_master_degree_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 五年碩申請 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['五年碩申請'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def doctor_admission(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 逕博相關規定 from \
            dbo.系所申請與轉換 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['逕博相關規定'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def graguated_information(mtext):
    if len(mtext.split('/')) != 6 or mtext.split('/')[2] == '沒指定' or mtext.split('/')[2] == '':
        return repair_function(mtext.split('/')[0])
    else:
        campus = mtext.split('/')[1]
        academy = mtext.split('/')[2]
        department = mtext.split('/')[3]
        education = mtext.split('/')[4]
        group = mtext.split('/')[5]

        if education == '大學部':
            education = '沒指定'

        if education == '沒指定':
            if department == '沒指定':
                return repair_function(mtext.split('/')[0])
            result = pd.read_sql("SELECT 學歷 from dbo.系所畢業規定 \
                    WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                    '%" + department + "%';", cnxn)

            for edu in result['學歷']:
                if edu != '沒指定' and department != '沒指定':
                    return TemplateSendMessage(
                        alt_text='請問是' + department + '的碩士班還是博士班的畢業資格呢？',
                        template=ButtonsTemplate(
                            title=department + '的畢業資格？',
                            text='請問是' + department + '的碩士班還是博士班的畢業資格呢？',
                            actions=[
                                MessageTemplateAction(
                                    label='碩士班',
                                    text='@系所畢業規定/' + campus + '/' + academy + '/' + department + '/碩士班/' + group
                                ),MessageTemplateAction(
                                    label='博士班',
                                    text='@系所畢業規定/' + campus + '/' + academy + '/' + department + '/博士班/' + group
                                )
                            ]
                        )
                    )

        if group == '沒指定':
            result = pd.read_sql("SELECT 組別 from dbo.系所畢業規定 \
                    WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
                    '%" + department + "%' AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE \
                    '%" + education + "%');", cnxn)

            gp_choice = []
            for gp in result['組別']:
                if gp != '沒指定':
                    append_col = CarouselColumn(
                        title=gp,
                        text='想詢問' + gp + '的畢業規定嗎？',
                        actions=[
                            MessageTemplateAction(
                                label='詢問' + gp,
                                text='@系所畢業規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + gp
                            )
                        ]
                    )
                    if len(gp_choice) == 0:
                        gp_choice.append(append_col)
                    elif append_col not in gp_choice:
                        gp_choice.append(append_col)

            if len(gp_choice) > 0 and len(gp_choice) < 11:
                rmtext = '請問是什麼組別呢？'
                Carousel_template = TemplateSendMessage(
                    alt_text=rmtext,
                    template=CarouselTemplate(
                        columns=gp_choice
                    )
                )

                return [
                    TextSendMessage(rmtext),
                    Carousel_template
                ]
            # Never Reach Here
            elif len(gp_choice) > 11:
                return TextSendMessage('組別超過十個垃圾Line api不能顯示QQ')

        if education != '沒指定':
            if group != '沒指定':
                result = pd.read_sql("SELECT 畢業相關項目 from dbo.系所畢業規定\
                        WHERE 校區 LIKE '%" + campus + "%'\
                        AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
                        AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
                        AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
                        AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%');", cnxn)
            else:
                result = pd.read_sql("SELECT 畢業相關項目 from dbo.系所畢業規定 \
                        WHERE 校區 LIKE '%" + campus + "%'\
                        AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
                        AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
                        AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
                        AND 組別 LIKE '%沒指定%';", cnxn)
        else:
            if group != '沒指定':
                result = pd.read_sql("SELECT 畢業相關項目 from dbo.系所畢業規定 \
                        WHERE 校區 LIKE '%" + campus + "%'\
                        AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
                        AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
                        AND 學歷 LIKE '%沒指定%'\
                        AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')", cnxn)
            else:
                result = pd.read_sql("SELECT 畢業相關項目 from dbo.系所畢業規定 \
                        WHERE 校區 LIKE '%" + campus + "%'\
                        AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
                        AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
                        AND 學歷 LIKE '%沒指定%'\
                        AND 組別 LIKE '%沒指定%';", cnxn)

        asked_organ = ''
        if academy != '沒指定':
            asked_organ = asked_organ + academy
        if department != '沒指定':
            asked_organ = asked_organ + department
        if education != '沒指定':
            asked_organ = asked_organ + education
        if group != '沒指定':
            asked_organ = asked_organ + group

        question = '畢業規定'
        if mtext.split('/')[0] == '口試及離校手續':
            question = '口試'
        elif mtext.split('/')[0] == '修課年限':
            question = '修課年限'

        question_type = []
        for q_type in result['畢業相關項目']:
            if question != '畢業規定':
                if question == q_type:
                    question_type.append(CarouselColumn(
                    title=q_type,
                    text='想詢問' + asked_organ + '的' + q_type + '嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + q_type,
                            text='@詢問畢業規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group + '/' + q_type
                        )
                    ]
                ))
            else:
                question_type.append(CarouselColumn(
                    title=q_type,
                    text='想詢問' + asked_organ + '的' + q_type + '嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問' + q_type,
                            text='@詢問畢業規定/' + campus + '/' + academy + '/' + department + '/' + education + '/' + group + '/' + q_type
                        )
                    ]
                ))

    if len(question_type) == 0:
        return TextSendMessage('並沒有關於' + asked_organ + '的' + question + '相關資訊喔！或是可能再把系所名稱再清楚一些講出來！')

    rmtext = '請問要詢問' + asked_organ + '的什麼問題呢？'
    Carousel_template = TemplateSendMessage(
        alt_text=rmtext,
        template=CarouselTemplate(
            columns=question_type
        )
    )

    return [
        TextSendMessage(rmtext),
        Carousel_template
    ]


def ask_graguated_information(mtext):
    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]
    group = mtext.split('/')[5]
    question_type = mtext.split('/')[6]

    result = pd.read_sql("SELECT 項目畢業規定 from dbo.系所畢業規定 \
            WHERE 校區 LIKE '%" + campus + "%'\
            AND (學院 = '" + academy + "' OR 學院 LIKE '%沒指定%')\
            AND (系所 LIKE '%" + department + "%' OR 系所 LIKE '%沒指定%')\
            AND (學歷 LIKE '%沒指定%' OR 學歷 LIKE '%" + education + "%')\
            AND (組別 LIKE '%沒指定%' OR 組別 LIKE '%" + group + "%')\
            AND 畢業相關項目 = '" + question_type + "';", cnxn)

    message = result['項目畢業規定'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + mtext + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + mtext + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + mtext + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def show_course(mtext, user_question):

    if len(mtext.split('/')) != 6 or mtext.split('/')[2] == '沒指定' or mtext.split('/')[2] == '':
        return repair_function(mtext.split('/')[0])

    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 課程種類一覽 from \
            dbo.系所課程相關 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['課程種類一覽'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]

def course_exemption(mtext, user_question):

    if len(mtext.split('/')) != 5 or mtext.split('/')[2] == '沒指定' or mtext.split('/')[2] == '':
        return repair_function(mtext.split('/')[0])

    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 課程免修 from \
            dbo.系所課程相關 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['課程免修'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def no_block_course(mtext, user_question):

    if len(mtext.split('/')) != 5 or mtext.split('/')[2] == '沒指定' or mtext.split('/')[2] == '':
        return repair_function(mtext.split('/')[0])

    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 課程免擋修 from \
            dbo.系所課程相關 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['課程免擋修'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def archaeological_question(mtext, user_question):

    if len(mtext.split('/')) != 5 or mtext.split('/')[2] == '沒指定' or mtext.split('/')[2] == '':
        return repair_function(mtext.split('/')[0])

    campus = mtext.split('/')[1]
    academy = mtext.split('/')[2]
    department = mtext.split('/')[3]
    education = mtext.split('/')[4]

    if education != '碩士在職專班':
        education = '沒指定'

    result = pd.read_sql("SELECT 考古題相關 from \
            dbo.系所課程相關 WHERE 學院 LIKE '%" + academy + "%' AND 系所 LIKE \
            '%" + department + "%' AND 學歷 LIKE '%" + education + "%';", cnxn)

    message = result['考古題相關'][0]
    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        TextSendMessage(message),
        feedback
    ]


def campus_map(mtext):
    campus = mtext.split('/')[1]
    map_category = mtext.split('/')[2]
    if map_category == '停車地圖':
        return TemplateSendMessage(
            alt_text = '停車地圖',
            template = ImageCarouselTemplate(
                columns = [
                    ImageCarouselColumn(
                        image_url = 'https://imgur.com/0DypDzl.jpg',
                        action = MessageTemplateAction(
                            label = "光復校區停車地圖",
                            text = "@光復校區停車地圖"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url = 'https://imgur.com/W6rJJR2.jpg',
                        action = MessageTemplateAction(
                            label = "陽明校區停車地圖",
                            text = "@陽明校區停車地圖"
                        )
                    )
                ]
            )
        )
    elif map_category == 'LOOPLUS地圖':
        return TextSendMessage(text='小幫手目前還沒有LOOPLUS的資訊喔！')
    else:
        return repair(mtext.split('/')[0])


def get_gym_crowd(user_question):
    import urllib.request as req
    url_gym_crowd = 'https://swimpool.nctu.edu.tw/NCTUGym/index.php/crowd/GetGymCrowd'
    url_gym_crowd_line = 'https://swimpool.nctu.edu.tw/NCTUGym/index.php/crowd/GetGymLineCrowd'

    # create a Request object with Request Header
    request_gym_crowd=req.Request(url_gym_crowd, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })

    with req.urlopen(request_gym_crowd) as response:
        data_gym_crowd = response.read()

    with req.urlopen(url_gym_crowd_line) as response:
        data_gym_crowd_line = response.read()

    import json
    data_gym_crowd_json = json.loads(data_gym_crowd)
    data_gym_crowd_line_json = json.loads(data_gym_crowd_line)

    reply_msg = "目前游泳館健身房有" + data_gym_crowd_json['crowd'] + "人\n\n資料更新時間：\n" + data_gym_crowd_json['time']
    message = TextSendMessage(reply_msg)

    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        message,
        feedback
    ]


def get_pool_crowd(user_question):
    import urllib.request as req
    url_pool_crowd = 'https://swimpool.nctu.edu.tw/NCTUGym/index.php/crowd/GetPoolCrowd'

    # create a Request object with Request Header
    request_pool_crowd=req.Request(url_pool_crowd, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })

    with req.urlopen(request_pool_crowd) as response:
        data_pool_crowd = response.read()

    import json
    data_pool_crowd_json = json.loads(data_pool_crowd)

    reply_msg = "目前游泳池有：" + data_pool_crowd_json['crowd'] + "人\n\n資料更新時間：\n" + data_pool_crowd_json['time']
    message = TextSendMessage(reply_msg)

    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        message,
        feedback
    ]


def restaurant(mtext):
    if (len(mtext.split('/')) < 3):
        campus = '沒指定'
        restaurant = mtext.split('/')[1]
    else:
        campus = mtext.split('/')[1]
        restaurant = mtext.split('/')[2]
    if (restaurant == '沒指定' or restaurant == ''):
        if (campus == '沒指定' or campus == ''):
            return TemplateSendMessage(
                alt_text='請選擇校區',
                template=ButtonsTemplate(
                    title='請選擇校區',
                    text='想知道哪個校區的學餐資訊呢？',
                    actions=[
                        MessageTemplateAction(
                            label='交大校區',
                            text='@學生餐廳/交大校區/沒指定'
                        ),
                        MessageTemplateAction(
                            label='陽明校區',
                            text='@學生餐廳/陽明校區/沒指定'
                        )
                    ]
                )
            )
        else:
            result = pd.read_sql("SELECT 學生餐廳 from dbo.學生餐廳資訊 \
                    WHERE 校區 LIKE '%" + campus + "%'", cnxn)
            restaurant_list = []
            for rest in result['學生餐廳']:
                tmp_list = CarouselColumn(
                    title=rest,
                    text='想詢問' + rest + '的資訊嗎？',
                    actions=[
                        MessageTemplateAction(
                            label='詢問這裡',
                            text='@學生餐廳/' + campus + '/' + rest
                        )
                    ]
                )
                if not (tmp_list in restaurant_list):
                    restaurant_list.append(tmp_list)
            return TemplateSendMessage(
                alt_text='請選擇餐廳',
                template=CarouselTemplate(
                    columns=restaurant_list
                )
            )
    else:
        result = pd.read_sql("SELECT 餐廳名稱 from dbo.學生餐廳資訊 \
                WHERE 學生餐廳 LIKE '%" + restaurant + "%'", cnxn)
        restaurant_name_list = []
        for restaurant_name in result['餐廳名稱']:
            restaurant_name_list.append(CarouselColumn(
                title=restaurant_name,
                text='想詢問' + restaurant_name + '的資訊嗎？',
                actions=[
                    MessageTemplateAction(
                        label='營業時間',
                        text='@詢問學生餐廳/' + restaurant_name + '/' + '營業時間'
                    ),
                    MessageTemplateAction(
                        label='查看菜單',
                        text='@詢問學生餐廳/' + restaurant_name + '/' + '菜單網址'
                    ),
                    MessageTemplateAction(
                        label='查看目前人潮',
                        text='@詢問學生餐廳/' + restaurant_name + '/' + '查看目前人潮'
                    )
                ]
            ))
        return TemplateSendMessage(
            alt_text='請選擇餐廳',
            template=CarouselTemplate(
                columns=restaurant_name_list
            )
        )


def ask_restaurant(mtext, user_question):
    restaurant = mtext.split('/')[1]
    action = mtext.split('/')[2]

    if action == '查看目前人潮':
        import populartimes, json
        from datetime import date, datetime
        import calendar
        # 取得今天星期幾
        today = calendar.day_name[date.today().weekday()]
        # 取得現在幾點
        now_clock = int(datetime.now().strftime("%H"))
        place_id = pd.read_sql("SELECT 地點ID from dbo.學生餐廳資訊 \
                WHERE 餐廳名稱 LIKE '%" + restaurant + "%'", cnxn)['地點ID'][0]
        populartimes_json = populartimes.get_id(API_KEY, place_id)
        for days in populartimes_json['populartimes']:
            if days['name'] == today:
                if days['data'][now_clock] == 0:
                    popular_level = '休息中'
                elif days['data'][now_clock] <= 25:
                    popular_level = '通常非繁忙時段'
                elif days['data'][now_clock] <= 50:
                    popular_level = '通常略為繁忙'
                elif days['data'][now_clock] <= 75:
                    popular_level = '通常有點繁忙'
                elif days['data'][now_clock] <= 25:
                    popular_level = '通常極為繁忙'
                rmtext = '根據Google Map的統計\n目前' + restaurant + '為' + popular_level
                message = TextSendMessage(rmtext)

    else:
        result = pd.read_sql("SELECT " + action + " from dbo.學生餐廳資訊 \
                WHERE 餐廳名稱 LIKE '%" + restaurant + "%'", cnxn)

        if action == '營業時間':
            message = TextSendMessage(result[action][0])
        elif action == '菜單網址':
            message = ImageSendMessage(original_content_url=result[action][0], preview_image_url=result[action][0])

    feedback = TemplateSendMessage(
        alt_text='請問答案對您是有幫助的嗎？',
        template=ButtonsTemplate(
            title='請問答案對您是有幫助的嗎？',
            text='請問答案對您的問題【' + user_question + '】是有幫助的嗎？',
            actions=[
                MessageTemplateAction(
                    label='有幫助',
                    text='@答案回饋(|)' + user_question + '(|)有幫助'
                ), MessageTemplateAction(
                    label='沒幫助',
                    text='@答案回饋(|)' + user_question + '(|)沒幫助'
                )
            ]
        )
    )
    return [
        message,
        feedback
    ]


def answer_feedback(mtext):
    from datetime import datetime
    time =datetime.now().strftime("%Y%m%d%H%M%S")
    question = mtext.split('(|)')[1]
    feedback = mtext.split('(|)')[2]
    d={'Time':[time], 'Question':[question], 'Feedback':[feedback]}
    table = pd.DataFrame(data=d)
    table.to_sql("答案回饋",con=engine,index=False, if_exists='append')
    if feedback == '沒幫助':
        return TemplateSendMessage(
            alt_text='有意願的話再麻煩您透過【問題回饋】告知我們詳細問題',
            template=ButtonsTemplate(
                title='感謝您的回饋',
                text='有意願的話再麻煩您透過【問題回饋】告知我們詳細問題',
                actions=[
                    MessageTemplateAction(
                        label='問題回饋',
                        text='@問題回饋'
                    )
                ]
            )
        )
    return TextSendMessage('感謝您的回饋！')


def repair_function(intent):
    getRepair = "SELECT Repair from dbo.repair_table WHERE Intent = '\n" + intent + "';"
    repair = pd.read_sql(getRepair,cnxn)
    print("Intent 「" + intent + "」 getting repair")
    if repair.empty or repair["Repair"][0] == '':
        print("Intent [" + intent + "]:Can not find answer in repair_table")
        message = "小幫手無法辨識您想問的是不是跟【"+ intent +"】相關的問題，再麻煩您換句話說說看！\n\n或也可以透過【問題回饋】告知我們！謝謝您！"
    else :
        message=repair["Repair"][0]
    return TextSendMessage(message)


def check_if_button_click(mtext):
    if ('@✦★#'.find(mtext[0]))==-1:
        #去掉文字的空白
        mtext_split = mtext.split(' ')
        mtext = ''
        for m in mtext_split:
            mtext += m
        mtext_split = mtext.split('\n')
        mtext = ''
        for m in mtext_split:
            mtext += m

        mtext = muterun_js('luis_sheet/get_db_intent.js ' + mtext).stdout.decode('utf-8')

    return mtext

# 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
if __name__ == '__main__':
    app.run()
