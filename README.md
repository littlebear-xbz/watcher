# watcher
监控mysql数据库，linux命令等

## 注意
> watcher.exe, conf/  log/  一个文件和这两个目录需要放在同一目录下

## 打包
可以使用pyinstaller 打包
依赖的包有：
1. pymysql
2. paramiko
3. smtplib


### 1.监控mysql表

1. 在conf/watcher.json文件中配置你想要监控的mysql数据库信息
2. 将服务添加到定时任务即可

### 2.监控shell程序

1. 在conf/watcher.json文件中配置你想要执行的linux脚本
2. 将服务添加定时任务即可
