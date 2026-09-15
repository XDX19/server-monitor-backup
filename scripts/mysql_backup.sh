#!/bin/bash
set -o pipefail

# mysql_backup.sh —— MySQL 自动备份脚本
# 功能：备份数据库、保留最近7天、上传至阿里云OSS
#
#加载配置（如果存在）
if [ -f "$(dirname "$0")/config.sh" ]; then
    source "$(dirname "$0")/config.sh"
fi

# 检查必要变量
if [ -z "$DB_USER" ] || [ -z "$DB_PASS" ]; then
    echo "错误：请先配置 config.sh"
    exit 1
fi

# 备份目录
BACKUP_DIR="/server-monitor-backup/backup/mysql"

# 保留天数
RETENTION_DAYS=7

# 时间戳
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/mysql_backup_${DATE}.sql.gz"


# ===== 创建备份目录 =====
mkdir -p "$BACKUP_DIR"

# ===== 执行备份 =====
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 开始备份..."

# 使用 mysqldump 备份并压缩
mysqldump -u$DB_USER -p$DB_PASS -h$DB_HOST $DB_NAME | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] 备份成功: $BACKUP_FILE"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] 备份失败！"
    exit 1
fi

# ===== 清理过期备份（保留最近7天）=====
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 清理 $RETENTION_DAYS 天前的备份..."
find "$BACKUP_DIR" -type f -name "mysql_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# ===== 上传至阿里云 OSS =====
if [ "$ENABLE_OSS_UPLOAD" = true ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] 开始上传至 OSS..."
    
    # 检查 ossutil 是否安装
    if command -v ossutil &> /dev/null; then
        ossutil cp "$BACKUP_FILE" "$OSS_BUCKET/$OSS_PATH" -f
        if [ $? -eq 0 ]; then
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] OSS 上传成功"
        else
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] OSS 上传失败"
        fi
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ossutil 未安装，跳过 OSS 上传"
    fi
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] 备份任务完成"
