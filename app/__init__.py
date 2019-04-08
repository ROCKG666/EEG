# -*- coding=utf-8 -*-
from flask import Flask
import pymysql
from . import config, utils
from flask_login import LoginManager
from .userAdmin import admin
from .exts import db


pymysql.install_as_MySQLdb()


# 创建登陆管理对象
login_manager = LoginManager()
# 设置session的保护强度
login_manager.session_protection = 'strong'
# 指定了登录页面的视图函数
login_manager.login_view = 'login'
# 指定了提供用户登录的提示信息
login_manager.login_message = '请登录'


def create_app():
    """"create a flask application and config it
    """
    app = Flask(__name__)
    app.config.from_object(config)
    # 初始化数据库， db=SQLAlchemy(app)
    db.init_app(app)
    # 初始化后台管理对象 admin=Admin(app)
    # 初始化登陆管理对象
    login_manager.init_app(app)
    # 推送应用上下文
    app.app_context().push()
    utils.set_log(app)
    # 必须要推送应用上下文后才能操作db
    # db.drop_all()
    # db.create_all()
    admin.init_app(app)

    # app关联蓝图程序
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .addData import addData
    app.register_blueprint(addData)
    from .getData import getData
    app.register_blueprint(getData)

    return app

