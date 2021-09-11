# coding: utf-8
import time
from Naked.toolshed.shell import muterun_js

mtext = '-'

while mtext != '':
    if mtext != '-':
        start_time = time.time()
        mtext = muterun_js('luis_sheet/get_db_intent.js ' + mtext).stdout.decode('utf-8')
        finish_time = time.time()
        print("Total get Intent time: ", finish_time - start_time)
        print("Result: ", mtext)
        print()
    else:
        print("測試中...")
        try:
            mtext = muterun_js('luis_sheet/get_db_intent.js 我想畢業').stdout.decode('utf-8')
            if (mtext == '系所畢業資格/沒指定/沒指定/沒指定/沒指定/沒指定'):
                print('環境OK!\n')
            else:
                print('環境沒問題，但Luis的判斷好像出事了...\n用其他文字測試一下\n')
        except:
            print('出事ㄌQQ\n檢查一下哪個步驟沒做好！')
            import sys
            sys.exit()
    mtext = input('請輸入要測試的文字(若要結束請直接按Enter or Return)：')
