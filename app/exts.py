# -*- coding=utf-8 -*-
"""导包中间文件，防止python循环导入"""
from flask_sqlalchemy import SQLAlchemy


# 为项目创建SQLAlchemy实例，可以通过db对象操作数据库
db = SQLAlchemy()


