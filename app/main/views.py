# -*- coding=utf8 -*-
from flask import json
from flask import request, jsonify, render_template
from flask_login import login_user
from . import main
from app import login_manager
from app.models import *
from .. import utils
from flask import current_app

# 注册接口已废弃
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


# 微信登陆接口-第二次登陆
@main.route('/wx_login/', methods=['GET', 'POST'])
def we_login():
    if request.method == "GET":
        return render_template("login.html")

    nickName = request.values.get("nickName")
    phone_num = request.values.get("phone_num")
    password = request.values.get("password")
    photo = request.values.get("avatarUrl")

    user_info = {
        "nickName": nickName,
        "phone_num": phone_num,
        "password": password,
        "photo": photo,
    }

    # 校验photo不为空
    if not photo:
        msg = "<%s, %s>头像URL为空, 请核查" %(nickName, phone_num)
        current_app.logger.error(msg)
        user_info['msg'] = "avatarUrl is None"
        return utils.make_resp(json.dumps(user_info), status=201)

    # 查询用户是否已经报名某课程
    course_entry = CoursesEntry.query.filter_by(phone_num=phone_num).first()

    if not course_entry:
        msg = "用户<%s | %s> 未报名课程" % (nickName, phone_num)
        current_app.logger.error(msg)
        user_info['msg'] = "Can't login, You Have Not Signed Up A Course"
        return utils.make_resp(json.dumps(user_info), status=201)
    # 如果用户不为空并且密码正确
    elif course_entry and course_entry.password == password:
        # 查询用户是否已经登陆过
        user = Users.query.filter_by(phone_num=phone_num).first()
        # 创建user, 存入数据库
        if not user:
            user = Users(**user_info)
            db.session.add(user)
            try:
                db.session.commit()
            except Exception as e:
                msg = "存入数据库失败，userinfo is %s err:%s" % (user_info,  str(e))
                current_app.logger.error(msg)
                return utils.make_resp(json.dumps(msg), status=500)

            else:
                # 登陆用户
                login_user(course_entry)
                msg = "用户登陆成功，userinfo: %s" % user_info
                current_app.logger.info(msg)
        user_info['msg'] = "success"
        return jsonify(user_info)
    else:
        msg = "用户名或密码错误, <%s | %s>" % (nickName, phone_num)
        current_app.logger.error(msg)
        user_info['msg'] = "用户名或密码错误"
        return utils.make_resp(json.dumps(user_info), status=201)


# 测试用户是否已经报名某课程
@main.route('/login_test/', methods=['GET', 'POST'])
def login_test():
    if request.method == "GET":
        return render_template("login.html")

    phone_num = request.values.get("phone_num")
    password = request.values.get("password")

    # 查询用户是否已经报名某课程
    course_entry = CoursesEntry.query.filter_by(phone_num=phone_num, password=password).first()
    if course_entry:
        current_app.logger.info("电话号已报名某课程, <%s>" % phone_num)

        user_info = dict()
        user_info['phone_num'] = phone_num
        user_info['password'] = password
        user_info['msg'] = "success"
        return jsonify(user_info)

    else:
        msg = "电话号或密码错误, <%s>" % phone_num
        current_app.logger.error(msg)
        return utils.make_resp(json.dumps(msg), status=201)


@login_manager.user_loader
def load_user(userid):
    """如果已经登陆的用户 login_user(user) 返回其id"""
    print("load_user", userid)
    user = Users.query.filter_by(id=userid).first()
    return user


# test API
@main.route("/new_register/", methods=["POST"])
def new_register():
    """接收post请求， 请求的数据为'nickName'
    url为 http://39.108.166.132:8888/wx_register
    注册成功返回用户信息，响应码为200
    注册失败返回失败的消息信息，响应码为201或500
    """
    print('前端的数据：', request.values)
    # 获取前端传递的数据,全部封装在request之中
    nickName = request.values.get("nickName")
    user = db.session.query(Users).filter_by(nickName=nickName).first()
    print("*******", user)
    if user:
        # 如果微信用户已存在，查询并返回此用户的信息， 响应码为201
        msg = "微信用户%s 存在" % nickName
        user_info = {
            "msg": msg,
            "nickName": nickName,
            "username": user.username,
        }
        current_app.logger.error(msg)
        return jsonify(user_info)
    # 如果用户不存在，继续获取信息并存储
    # 生成用户信息-->字典格式
    else:
        msg = "微信用户%s 不存在" % nickName
        user_info = {
            "msg": msg,
            "nickName": None,
            "username": None,
        }
        current_app.logger.error(msg)
        return jsonify(user_info)

