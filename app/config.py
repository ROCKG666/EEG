# -*- coding=utf-8 -*-
""" 项目的配置文件，做整个项目的基础配置
    微信表情占4个字节，mysql的字符集要设置为utf8mb4
"""
import os


DEBUG = True  # 调试模式,生产环境注释即可
# 配置数据库的连接字符串, 设置字符集为utf8mb4
SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost:3306/minisql?charset=utf8mb4"
# 配置数据库内容更新时自动提交
# SQLALCHEMY_COMMIT_ON_TEARDOWN = True
# 关闭提示
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 设置session密钥
SECRET_KEY = os.urandom(24)
# 解决返回json数据中的中文乱码， json模块必须使用flask.json
JSON_AS_ASCII = False


