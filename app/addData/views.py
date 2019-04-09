# -*- coding=utf8 -*-
import datetime

from flask import json
from flask import request, jsonify, make_response
from . import addData
from app.models import *
from flask import current_app
from app import utils


def add_school_model():
    school1 = {'user_id': 1, "name": "新东方", "building": "1993年", "principal": "俞敏洪", "photo": "/static/upload/schools/xdf-logo.jpg"}
    school2 = {"user_id": 2, "name": "学为贵", "building": "2010年", "principal": "刘洪波", "photo": "/static/upload/schools/xwg-logo.jpg"}
    school3 = {"user_id": 3, "name": "环球雅思", "building": "2001年", "principal": "张永琪", "photo": "/static/upload/schools/hqys-logo.png"}
    school4 = {"user_id": 4, "name": "趴趴雅思", "building": "2014年", "principal": "上海茵朗信息科技", "photo": "/static/upload/schools/ppys-logo.jpg"}
    schools = [school1, school2, school3, school4]
    for school_info in schools:
        school = Schools(**school_info)
        user_info = {
            "id": school_info["user_id"],
            "photo": school_info['photo'],
        }

        user = Users(**user_info)
        db.session.add_all([user, school])
        db.session.commit()
    schools = db.session.query(Schools).all()
    print(schools[0].name)
# add_school_model()


# 增加课程--此接口已废弃
@addData.route("/add_course", methods=["POST"])
def add_course():
    """增加课程接口，post请求中携带的data为：
    course_name：课程名
    category：课程类别
    content：课程的内容--url
    teacher_name：课程所属的学校
    teacher_name：课程对应的老师
    url: http://www.xiaochengxueeg.xyz:8888/add_course
    :return 所增加课程的详细信息
    """
    name = request.values.get("course_name")
    category = request.values.get("category")
    content = request.values.get("content")
    school_name = request.values.get("school_name")
    teacher_name = request.values.get("teacher_name")
    school = db.session.query(Schools).filter_by(name=school_name).first()
    teacher = db.session.query(Teachers).filter_by(name=teacher_name).first()
    course_info = {
        "name": name,
        "category": category,
        "content": content,
        "school": school_name,
        "teacher": teacher_name,
        "teacher_id": teacher.id,
        "school_id": school.id,
    }
    course = Courses(**course_info)
    db.session.add(course)
    try:
        db.session.commit()
        current_app.logger.info("添加课程%s成功" % name)
    except Exception as e:
        msg = "增加<%s>学校的 <%s>老师的 <%s>课程失败, error:%s" % (school_name, teacher_name, name, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)
    current_app.logger.info("增加<%s>学校的 <%s>老师的 <%s>课程成功" % (school_name, teacher_name, name))
    return jsonify(course_info)


# 发表评论
@addData.route("/make_comments/", methods=["POST", 'GET'])
def make_comments():
    """发表评论接口，post请求中携带的data为：
    nickName:微信名。代表学生
    course_id：课程的id
    content：评论的内容
    url: http://www.xiaochengxueeg.xyz:8888/make_comment
    :return 所增增加评论的详细信息
    """
    nickName = request.values.get("nickName")
    course_id = request.values.get("course_id")
    content = request.values.get("content")

    try:
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        course = db.session.query(Courses).filter_by(id=course_id).first()
    except Exception as e:
        msg = "获取用户%s/课程%s 信息失败，error:%s" % (nickName, course_id, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not course:
        msg = "%s课程不存在, 无法评论，请核对" % course_id
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    current = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    comment_info = {
        "user_id": user.id,
        "course_id": course_id,
        "content": content,
        "comment_time": current
    }
    comment = Comments(**comment_info)
    db.session.add(comment)
    try:
        db.session.commit()
        current_app.logger.info("<%s>评论课程<%s>成功, 评论内容：%s" % (nickName, course_id, content))
    except Exception as e:
        msg = "用户<%s>评论 课程<%s>失败, error:%s" % (nickName, course_id, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    comment_info['nickName'] = nickName
    comment_info['msg'] = "发表评论成功"
    return jsonify(comment_info)


# 存储脑电数据--original
@addData.route("/save_waves/", methods=["POST"])
def save_waves():
    """存储脑电数据接口，post请求中携带的data为：
    nickName:微信名用户名。代表学生
    course_id：脑电数据的课程名
    data：脑电数据
    url: http://www.xiaochengxueeg.xyz:8888/save_waves
    :return 所增加脑电数据的详细信息
    """
    username = request.values.get("username")
    course_id = request.values.get("course_id")
    data = request.values.get("data")

    try:
        # 根据nickName和username定位学生
        user = db.session.query(Users).filter_by(username=username).first()
        course = db.session.query(Courses).filter_by(id=course_id).first()
    except Exception as e:
        msg = "获取用户%s / 课程%s 信息失败，error:%s" % (username, course_id, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not user:
        msg = "%s用户不存在, 无法添加脑电数据，请核对" % username
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)
    if not course:
        msg = "%s课程不存在, 无法添加脑电数据，请核对" % course_id
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wave_info = {
        "nickName": user.nickName,
        "username": username,
        "user_id": user.id,
        "course_id": course_id,
        "course_name": course.name,
        "course_category": course.category,
        "course_avg_data": course.avg_data,
        "wave_data": data,
        "test_time": current
    }

    wave = Waves(**wave_info)
    print(wave_info)
    db.session.add(wave)
    db.session.flush()

    # 查找课程对应的所有脑电数据, 修改脑电数据
    course_waves = course.waves.all()

    totle_data = 0
    for wave in course_waves:
        data = wave.data
        if data is None:
            data = 0
        try:
            totle_data += float(data)
        except Exception as e:
            msg = "统计脑电数据%s失败, error:%s" % (data, str(e))
            current_app.logger.error(msg)
            return utils.make_resp(msg=json.dumps(msg), status=500)

    course_avg_data = totle_data / len(course_waves)
    course.avg_data = round(course_avg_data, 2)
    try:
        db.session.commit()
    except Exception as e:
        msg = "存储用户<%s> 的 <%s>课程 的脑电数据%s失败, error:%s" % (username, course_id, data, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)
    wave_info["msg"] = "存储脑电数据成功"
    return jsonify(wave_info)


# 微信存储脑电数据-new
@addData.route("/save_waves_by_wx/", methods=["POST"])
def save_waves_by_wx():
    """存储脑电数据接口，post请求中携带的data为：
    nickName:微信名用户名。代表学生
    course_id：脑电数据的课程名
    url: http://www.xiaochengxueeg.xyz:8888/save_waves
    :return 所增加脑电数据的详细信息
    """
    nickName = request.values.get("nickName")
    course_id = request.values.get("course_id")

    try:
        # 根据nickName和username定位学生
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        course = db.session.query(Courses).filter_by(id=course_id).first()
    except Exception as e:
        msg = "获取用户%s / 课程%s 信息失败，error:%s" % (nickName, course_id, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not user:
        msg = "%s用户不存在, 无法添加脑电数据，请核对" % nickName
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)
    if not course:
        msg = "%s课程不存在, 无法添加脑电数据，请核对" % course_id
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    # 定位学生和课程
    wave_info = {
        "nickName": nickName,
        "username": user.username,
        "user_id": user.id,
        "course_id": course_id,
        "course_name": course.name,
        "course_category": course.category,
        "course_avg_data": course.avg_data,
    }

    wave = Waves(**wave_info)
    db.session.add(wave)
    # db.session.flush()

    # 查找课程对应的所有脑电数据, 修改脑电数据
    # course_waves = course.waves.all()

    # totle_data = 0
    # for wave in course_waves:
    #     data = wave.data
    #     if data is None:
    #         data = 0
    #     try:
    #         totle_data += float(data)
    #     except Exception as e:
    #         msg = "统计脑电数据%s失败, error:%s" % (data, str(e))
    #         current_app.logger.error(msg)
    #         return utils.make_resp(msg=json.dumps(msg), status=500)
    #
    # course_avg_data = totle_data / len(course_waves)
    # course.avg_data = round(course_avg_data, 2)
    try:
        db.session.commit()
    except Exception as e:
        msg = "存储用户<%s> 的 <%s>课程 的脑电数据失败, error:%s" % (nickName, course_id, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)
    wave_info["msg"] = "操作成功，等待上传脑电数据。。。"
    return jsonify(wave_info)


# APP存储脑电数据-new
@addData.route("/save_waves_by_app/", methods=["POST"])
def save_waves_by_app():
    """存储脑电数据接口，post请求中携带的data为：
    username:app用户名。代表学生
    data：脑电数据
    url: http://www.xiaochengxueeg.xyz:8888/save_waves
    :return 所增加脑电数据的详细信息
    """
    username = request.values.get("username")
    data = request.values.get("data")

    try:
        # 根据nickName和username定位学生
        user = db.session.query(Users).filter_by(username=username).first()
    except Exception as e:
        msg = "获取用户%s 信息失败，error:%s" % (username, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not user:
        msg = "%s用户不存在, 无法添加脑电数据，请核对" % username
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    # 查找需要添加data的wave记录
    wave = Waves.query.filter(Waves.user_id == user.id, Waves.course_id != None, Waves.data == None).first()

    if not wave:
        msg = "需要添加脑电数据<%s, %s> 的记录不存在, 请核对" % (username, data)
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wave.test_time = current,
    wave.wave_data = data,

    db.session.flush()

    course = Courses.query.filter_by(id=wave.course_id).first()
    # 查找课程对应的所有脑电数据, 修改脑电数据
    course_waves = course.waves.all()

    totle_data = 0
    for wave in course_waves:
        data = wave.data

        if data is None:
            data = 0
        try:
            totle_data += float(data)
        except Exception as e:
            msg = "统计脑电数据%s失败, error:%s" % (data, str(e))
            current_app.logger.error(msg)
            return utils.make_resp(msg=json.dumps(msg), status=500)

    course_avg_data = totle_data / len(course_waves)
    course.avg_data = round(course_avg_data, 2)

    try:
        db.session.commit()
    except Exception as e:
        msg = "存储用户<%s> 的脑电数据失败, error:%s" % (username, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)
    return jsonify("success")
