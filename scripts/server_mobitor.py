#!/usr/bin/env python3
"""
服务器健康检查脚本 — 检查 CPU/内存/磁盘，异常时推送企业微信告警
"""

import psutil
import requests
import json
from datetime import datetime

# ===== 配置区 =====
THRESHOLDS = {
    "cpu_percent": 80,      # CPU 使用率阈值 (%)
    "memory_percent": 85,   # 内存使用率阈值 (%)
    "disk_percent": 90,     # 磁盘使用率阈值 (%)
    "disk_path": "/"        # 检查的磁盘路径
}

# 企业微信机器人 Webhook（替换为你的实际地址）
WEBHOOK_URL = "https://qyapi.weixin.qq.com/"

# ===== 采集函数 =====
def collect_metrics():
    """采集服务器各项指标"""
    metrics = {}
    
    # CPU
    metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
    metrics["cpu_count"] = psutil.cpu_count()
    
    # 内存
    mem = psutil.virtual_memory()
    metrics["memory_percent"] = mem.percent
    metrics["memory_total_gb"] = round(mem.total / 1024**3, 1)
    metrics["memory_used_gb"] = round(mem.used / 1024**3, 1)
    
    # 磁盘
    disk = psutil.disk_usage(THRESHOLDS["disk_path"])
    metrics["disk_percent"] = disk.percent
    metrics["disk_total_gb"] = round(disk.total / 1024**3, 1)
    metrics["disk_used_gb"] = round(disk.used / 1024**3, 1)

    return metrics

def check_thresholds(metrics):
    """检查是否超过阈值，返回告警列表"""
    alerts = []
    hostname = socket.gethostname()
    
    if metrics["cpu_percent"] > THRESHOLDS["cpu_percent"]:
        alerts.append(f"⚠️ CPU 使用率: {metrics['cpu_percent']}% (阈值: {THRESHOLDS['cpu_percent']}%)")
    
    if metrics["memory_percent"] > THRESHOLDS["memory_percent"]:
        alerts.append(f"⚠️ 内存使用率: {metrics['memory_percent']}% (阈值: {THRESHOLDS['memory_percent']}%)")
    
    if metrics["disk_percent"] > THRESHOLDS["disk_percent"]:
        alerts.append(f"⚠️ 磁盘使用率: {metrics['disk_percent']}% (阈值: {THRESHOLDS['disk_percent']}%)")
    
    return alerts

def send_wechat_alert(alerts, metrics):
    """发送企业微信告警"""
    if not alerts:
        return
    
    hostname = socket.gethostname()
    content = f"""## 🚨 服务器告警通知

**主机**: {hostname}
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 告警详情
{chr(10).join(alerts)}

### 当前指标
- CPU: {metrics['cpu_percent']}%
- 内存: {metrics['memory_used_gb']}GB / {metrics['memory_total_gb']}GB ({metrics['memory_percent']}%)
- 磁盘: {metrics['disk_used_gb']}GB / {metrics['disk_total_gb']}GB ({metrics['disk_percent']}%)
"""
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.json().get('errcode') == 0:
            print(f"[{datetime.now()}] 告警推送成功")
        else:
            print(f"[{datetime.now()}] 告警推送失败: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] 推送异常: {e}")

def main():
    metrics = collect_metrics()
    alerts = check_thresholds(metrics)
    if alerts:
        send_wechat_alert(alerts, metrics)
    else:
        print(f"[{datetime.now()}] 所有指标正常")

if __name__ == "__main__":
    import socket
    main()
