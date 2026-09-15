# 服务器监控与 MySQL 自动备份

一套轻量级的 Linux 服务器运维方案，包含：
- Python 服务器监控（CPU / 内存 / 磁盘），异常推送告警
- Shell MySQL 自动备份，保留最近 7 天，上传至阿里云 OSS
- Cron 定时调度

## 功能

- 实时监控 CPU、内存、磁盘使用率
- 超阈值自动推送告警（支持企业微信 / Server酱 / 邮件）
- MySQL 每日自动备份，本地保留 7 天
- 备份文件自动上传至阿里云 OSS
- ✅ Cron 定时调度，日志自动记录

## 目录结构

server-monitor-backup/  
├── README.md  
├── .gitignore  
├── config.example.sh          # 配置模板  
├── scripts/  
│   ├── server_monitor.py      # 监控脚本  
│   └── mysql_backup.sh        # 备份脚本  
├── cron/  
│   └── crontab.example        # crontab 示例  


## 环境要求

- OS: Ubuntu 20.04+ / Debian 11+
- Python: 3.8+
- MySQL: 5.7+ / 8.0+
- ossutil: 2.0+


# 部署步骤总结
## 1.安装依赖
    bash  
    pip install psutil requests   
    sudo apt update && sudo apt upgrade -y  #安装mysql  
    sudo apt install -y mysql-server  
    sudo systemctl status mysql             #设置开机自启动

## 2.配置

### 备份脚本配置
复制 `config.example.sh` 为 `config.sh`，填入你的实际配置:  

    bash
    cp config.example.sh config.sh  
    nano config / vim config.sh  


### 配置企业微信机器人
   **获取 Webhook URL**,填入 *WEBHOOK_URL = "https://qyapi.weixin.qq.com/"*



## 3.安装 ossutil：下载并配置阿里云 OSS 访问凭证

### OSS配置
    curl https://gosspublic.alicdn.com/ossutil/install.sh | sudo bash #下载安装ossutil
    ossutil config
**按提示输入你的 AccessKey ID、AccessKey Secret 和 Endpoint 即可**

## 4.设置 cron：crontab -e 添加定时任务

### 配置 cron

    bash
    crontab -e


（粘贴 crontab.example 的内容,注意文件路径是否与你的相同）

## 5.测试验证：手动执行脚本，确认备份和告警正常

# 验证测试
    bash
    手动测试监控脚本
    python3 /server-monitor-backup/scripts/server_monitor.py

    手动测试备份脚本
    bash /server-monitor-backup/scripts/mysql_backup.sh

    查看 cron 是否正常运行
    grep CRON /var/log/syslog | tail -20

    查看备份文件
    ls -lh /server-monitor-backup/backup/mysql/

    查看 OSS 是否上传成功
    ossutil ls oss://your-bucket-name/mysql-backup/


