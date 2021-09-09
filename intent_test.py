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
    mtext = input('請輸入要測試的文字(若要結束請直接按Enter or Return)：')
