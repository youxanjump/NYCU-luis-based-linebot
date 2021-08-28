# NYCU-luis-based-linebot
測試用linebot

- 看一下我main.py有import什麼，記得都要pip install一下
- 我的資料存取都是學校大數據中心的電腦，所以記得要連學校VPN才可以正常使用
- 因為資料庫是使用微軟的MSSQL，記得要裝driver，目前Apple M1晶片無法安裝（開虛擬機用Ubuntu應該都安全啦，不過我都是直接在Intel cpu下的macos環境執行，所以沒試過）

## intent_test.py
單純用來測試自然語言透過luis_sheet專案分析完後的結果

- 語意分析流程程式碼導讀
1. 將自然語言“mtext”丟進“luis_sheet/get_db_intent.js”中的function “getDBIntent”
2. 在這裡會將剛才傳進來的mtext打包成要餵給LUIS的Foramt，接著將其丟進目前 “util/for_get_db_intents/_get_db_intents.js”中的function “getDBIntents“
3. 接著跟著code的註解，應該能滿清楚每個function的功用

## main.py
- bot_config.py在我本人這邊，因為金曜都在這裡
- 要測試的話，去安裝[ngrok](https://ngrok.com)
- 執行ngrok
```shell
ngrok http 5000
```
- 將網址(https://的那個)貼到LINE DEVELOP帳號底下的Message API中的Webhook，最後加上"/CampusChatbot"
- 執行main.py
```shell
python main.py
```
