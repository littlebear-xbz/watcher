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

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import ConfigParser
import logging.config
import sys
import json
import datetime
import pymysql
import paramiko


CF = ConfigParser.ConfigParser()
CF.read('./conf/conf.conf')
logging.config.fileConfig("./conf/logger.conf")
logger = logging.getLogger("FileAndScreen")
reload(sys)
sys.setdefaultencoding('utf-8')

# 发送邮件的变量
msg_context = """"""
# 获取发送邮件内容
def get_context():
    # 读取配置文件
    try:
        with open('./conf/watcher.json','r') as f:
            watcher_confs = json.load(f)
        logger.info("成功加载watcher.json文件；")
    except Exception, e:
        logger.error("无法打开或读取sql配置文件，目标目录：'./conf/sqls.json'")
        logger.error(e)
        exit()
    for watcher_conf in watcher_confs:
        if watcher_conf.has_key('type'):
            if watcher_conf["type"] == "mysql":
                get_mysql_context(watcher_conf)
            elif watcher_conf["type"] == "shell":
                get_shell_context(watcher_conf)
            else:
                logger.error("无法处理的类型" + watcher_conf["type"])
        else:
            logger.error("无法识别的配置段" + watcher_conf)

# 配置为mysql的处理方案
def get_mysql_context(watcher_conf):
    logger.info("开始处理数据库：" + watcher_conf["dbcomment"])
    global msg_context
    msg_context = msg_context + "\n---------------------------------------\n"
    msg_context = msg_context + watcher_conf["dbcomment"] + '\n'
    try:
        host = watcher_conf["host"]
        port = watcher_conf["port"]
        user = watcher_conf["user"]
        passwd = watcher_conf["passwd"]
        db = watcher_conf["db"]
        sqls = watcher_conf["sqls"]
        conn = pymysql.connect(
            host=host, port=port, user=user,
            passwd=passwd, db=db
        )
        cursor = conn.cursor()
        logger.info("成功连接数据库：")
        logger.info(watcher_conf)
    except Exception, e:
        logger.error("不能连接配置的数据库：")
        logger.error(watcher_conf)
        logger.error(e)
        msg_add = "\n---------------------------------------\n"
        msg_add = msg_add + "不能连接配置的数据库:\n"
        msg_add = msg_add + str(watcher_conf) + "\n"
        msg_context = msg_context + msg_add
        return -1
    for sql in sqls:
        sql_e = sql["sql"]
        sql_c = sql["comment"]
        try:
            cursor.execute(sql_e)
            result = cursor.fetchall()
        except Exception, e:
            logger.error("无法执行sql语句" + sql_e)
            msg_context = msg_context + "---------------------------------------\n"
            msg_context = msg_context + sql_c + "：\n" + "无法执行语句:" + sql_e + "\n"
            continue
        msg_add = "---------------------------------------\n"
        msg_add = msg_add +  sql_c + "：\n" + str(result) + "\n"
        logger.info("增加邮件发送内容：" + msg_add)
        msg_context = msg_context + msg_add
    cursor.close()
    conn.close()

# 配置为shell的处理方案
def get_shell_context(watcher_conf):
    logger.info("开始处理脚本：" + watcher_conf["comment"])
    global msg_context
    msg_context = msg_context + "\n---------------------------------------\n"
    msg_context = msg_context + watcher_conf["comment"] + '\n'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = watcher_conf["host"]
    port = watcher_conf["port"]
    user = watcher_conf["user"]
    passwd = watcher_conf["passwd"]
    try:
        ssh.connect(host, port, user, passwd)
        logger.info("成功连接上主机：" + host)
    except Exception, e:
        logger.error("无法连接配置信息上的主机")
        msg_add = "\n---------------------------------------\n"
        msg_add = msg_add + "无法连接配置信息上的主机\n"
        msg_add = msg_add + str(watcher_conf) + "\n"
        msg_context = msg_context + msg_add
        return -1
    for cmd in watcher_conf["cmds"]:
        cmd_e = cmd["cmd"]
        cmd_c = cmd["comment"]
        stdin, stdout, stderr = ssh.exec_command(cmd_e)
        logger.info(cmd_e)
        msg_add = "---------------------------------------\n"
        msg_add = msg_add + cmd_c + "\n"
        for line in stdout.readlines():
            logger.info(line)
            msg_add = msg_add + line + "\n"
        msg_context = msg_context + msg_add
    ssh.close()


# -------------------------
# 邮件发送模块
# -------------------------
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def send_mail(msg_context):
    from_addr = '15337192267@163.com' # 写自己的账号
    password = '******' # 根据自己授权码来写
    subject = CF.get('email', 'subject') + str(datetime.date.today())
    # to_addr = 'littlebear.xbz@qq.com'
    to_addr = CF.get('email', 'email_to').split(',')
    from_name = CF.get('email', 'from')
    smtp_server = 'smtp.163.com'
    msg = MIMEText(msg_context, 'plain', 'utf-8')
    msg['From'] = _format_addr('{from_name} <{from_addr}>'.format(from_name=from_name,from_addr=from_addr))
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header(subject, 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.helo(smtp_server)
    server.ehlo(smtp_server)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


if __name__ == "__main__":
    get_context()
    send_mail(msg_context)

