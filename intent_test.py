# coding: utf-8

import sys
import numpy as np
import pandas as pd
import pyodbc
import time

mtext = "學校地圖"
start_time = time.time()

if ('@✦★#'.find(mtext[0])) == -1:
    mtext = muterun_js('luis_sheet/get_db_intent.js ' + mtext).stdout.decode('utf-8')

finish_time = time.time()
print("Total get Intent time: ", finish_time - start_time)
print(mtext)
intent = mtext.split('/')[0]
print(intent)
