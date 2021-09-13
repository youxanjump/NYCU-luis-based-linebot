# NYCU-luis-based-linebot
測試用linebot
## Getting Start
1. Clone the repository
```shell
git clone https://github.com/youxanjump/NYCU-luis-based-linebot.git
cd NYCU-luis-based-linebot
git clone https://github.com/youxanjump/luis_sheet.git
```
2. Create and Activate虛擬環境
```shell
virtualenv env
source env/bin/activate
```
3. 安裝python所需套件
  ```shell
  python -m pip install -r requirements.txt
  ```
4. 安裝Nodejs所需套件
```shell
cd luis_sheet
npm install
```
5. 安裝Microsoft ODBC driver
- 因為資料庫是使用微軟的MSSQL，記得要裝Microsoft ODBC driver（[for macOS](https://docs.microsoft.com/zh-tw/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15)、[for Windows](https://docs.microsoft.com/zh-tw/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15)、[for Linux](https://docs.microsoft.com/zh-tw/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15)）
6. 連入學校VPN(不一定要做)
- 資料存取都是學校大數據中心的電腦，所以記得要連學校VPN才可以正常使用，但如果在學校的話就不用特別連了([設定教學](https://it.nycu.edu.tw/it-services/networks/ssl-vpn/))
7. NYCU-luis-based-linebot/bot_config.py luis_sheet/config_LUIS.js luis_sheet/cred.json從大數據雲端下載
8. 測試Luis以及資料庫是否能正常運作
```shell
cd ..
python manage.py test
```
- 輸入任何「有關學校問題的自然語言」，輸出Intent以及所需參數
- 若無法判斷Intent則會回傳原本輸入的字句

## intent_test.py
單純用來測試自然語言透過luis_sheet專案分析完後的結果

- 語意分析流程程式碼導讀
1. 將自然語言“mtext”丟進“luis_sheet/get_db_intent.js”中的function “getDBIntent”
2. 在這裡會將剛才傳進來的mtext打包成要餵給LUIS的Foramt，接著將其丟進目前 “util/for_get_db_intents/_get_db_intents.js”中的function “getDBIntents“
3. 接著跟著code的註解，應該能滿清楚每個function的功用

## main.py
- bot_config.py在我本人這邊，因為金鑰都在這裡
- 要測試的話，去安裝[ngrok](https://ngrok.com)
- 執行ngrok
```shell
ngrok http 5000
```
- 將網址(https的那個)貼到LINE DEVELOP帳號底下的Message API中的Webhook，最後加上"/CampusChatbot"
- 執行main.py
```shell
python manage.py runserver
```
