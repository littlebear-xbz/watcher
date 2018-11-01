# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Administrator'
__mtime__ = '2018-10-26'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""

import pymysql
import datetime

msg_context = """"""
# 获取发送邮件内容
def get_context():
    mysql_conn = pymysql.connect(host='localhost', port=3306,
                                 user='l',
                                 passwd='l@Mysql01',
                                 db='kapc_hk_cr'
                                 )
    mysql_cursor = mysql_conn.cursor()
    # 全部需要查询的sql语句
    sqls = ["select count(*) from ods_hk_cr_vechile_rt"]
    for sql in sqls:
        mysql_cursor.execute(sql)
        results = mysql_cursor.fetchall()
        cnt = results[0][0]
        global msg_context
        msg_context = msg_context + "\n" + "当天卡口原始数据（ods_hk_cr_vechile_rt）: " + str(cnt)
    mysql_cursor.close()
    mysql_conn.close()

get_context()

print(msg_context)