"""数据库与服务器配置"""
import os

# MySQL 连接
MYSQL_HOST     = os.environ.get("CAIPU_DB_HOST", "127.0.0.1")
MYSQL_PORT     = int(os.environ.get("CAIPU_DB_PORT", "3306"))
MYSQL_USER     = os.environ.get("CAIPU_DB_USER", "root")
MYSQL_PASSWORD = os.environ.get("CAIPU_DB_PASSWORD", "")
MYSQL_DB       = os.environ.get("CAIPU_DB_NAME", "caipu_app")
MYSQL_CHARSET  = "utf8mb4"

# 服务器
DEFAULT_PORT = int(os.environ.get("CAIPU_PORT", "5000"))
