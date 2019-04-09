# -*- coding=utf8 -*-
from flask import json
from flask import request, jsonify, render_template
from flask_login import login_user
from . import main
from app import login_manager
from app.models import *
from .. import utils
from flask import current_app


# 注册app用户
@main.route('/app_register/', methods=["POST"])
def app_register():
    """接受post请求， 请求的数据为'nickName', 'username', 'password'
        url为 http://39.108.166.132:8888/app_register
    """
    current_app.logger.info("接收到数据：", request.values)
    nickName = request.values.get("nickName")
    user = db.session.query(Users).filter_by(nickName=nickName).first()
    # 如果微信名不存在，响应码为201
    if not user:
        msg = "注册app的用户名 %s 不存在" % nickName
        current_app.logger.error(msg)
        return utils.make_resp(json.dumps(msg), status=201)
    # 获取注册app的用户名和密码
    username = request.values.get("username")
    password = request.values.get("password")

    user.username = username
    user.password = password
    user_info = {
        "nickName": nickName,
        "username": username,
    }
    try:
        db.session.commit()
        user_info["id"] = user.id
        user_info["msg"] = "注册成功"
        current_app.logger.info("微信用户%s 注册app用户%s成功, info-->%s" % (nickName, username, user_info))
        return jsonify(user_info)
    except Exception as e:
        msg = "微信用户%s 注册app用户%s失败， err:%s" % (nickName, username, e)
        utils.make_resp(json.dumps(msg), status=500)
        current_app.logger.error(msg)


# 注册微信用户->选择用户类型，存入数据库
@main.route("/wx_register/", methods=["POST"])
def wx_register():
    """接收post请求， 请求的数据为'nickName'
    url为 http://39.108.166.132:8888/wx_register
    注册成功返回用户信息，响应码为200
    注册失败返回失败的消息信息，响应码为201或500
    """
    print('前端的数据：', request.values)
    # 获取前端传递的数据,全部封装在request之中
    nickName = request.values.get("nickName")
    photo = request.values.get("avatarUrl")
    user = db.session.query(Users).filter_by(nickName=nickName).first()
    if user:
        # 如果微信用户已存在，查询并返回此用户的信息， 响应码为201
        msg = "微信用户%s 已存在, 注册失败" % nickName
        user_info = {
            "msg": msg,
            "id": user.id,
            "nickName": user.nickName,
            "username": user.username,
            "photo": user.photo,
        }
        current_app.logger.error(msg)
        return utils.make_resp(json.dumps(user_info), status=201)
    # 如果用户不存在，继续获取信息并存储
    # 生成用户信息-->字典格式
    user_info = {
        "nickName": nickName,
        "photo": photo,
    }
    user = Users(**user_info)
    db.session.add(user)

    try:
        db.session.commit()
        current_app.logger.info("微信用户%s 注册成功, info-->%s" % (nickName, user_info))
        user_info['msg'] = "注册成功"
        user_info['id'] = user.id
        return jsonify(user_info)
    except Exception as e:
        errmsg = "用户%s存入users表失败, error-->%s" % (nickName, str(e))
        current_app.logger.error(errmsg)
        resp = utils.make_resp(msg=json.dumps(errmsg), status=500)
        return resp


@main.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.values.get("username")
    password = request.values.get("password")
    user = Users.query.filter_by(username=username).first()
    # 如果用户不为空并且密码正确
    if user is not None and user.password == password:
        # 登陆用户
        login_user(user)
        msg = "用户%s 登陆成功" % username
        current_app.logger.info(msg)
        # return jsonify(msg)
        return jsonify("success")
    else:
        msg = "用户名或密码错误, %s" % username
        current_app.logger.info(msg)
        return utils.make_resp(json.dumps(msg), status=201)


@login_manager.user_loader
def load_user(userid):
    """如果已经登陆的用户 login_user(user) 返回其id"""
    print("load_user", userid)
    user = Users.query.filter_by(id=userid).first()
    return user
