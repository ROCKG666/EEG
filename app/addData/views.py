# -*- coding=utf8 -*-
import datetime

from flask import json
from flask import request, jsonify, make_response
from . import addData
from app.models import *
from flask import current_app
from app import utils


# 发表评论
@addData.route("/make_comments/", methods=["POST", 'GET'])
def make_comments():
    """发表评论接口，post请求中携带的data为：
    phone_num:电话号。代表学生
    course_id：课程的id
    content：评论的内容
    url: http://www.xiaochengxueeg.xyz:8888/make_comment
    :return 所增增加评论的详细信息
    """
    phone_num = request.values.get("phone_num")
    course_id = request.values.get("course_id")
    content = request.values.get("content")

    try:
        course_entry = CoursesEntry.query.filter_by(phone_num=phone_num, course_id=course_id).first()
    except Exception as e:
        msg = "获取用户%s/课程%s 信息失败，error:%s" % (phone_num, course_id, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not course_entry:
        # 没有权限 status=201 msg=Can't Make Comment, Permission Denied
        msg = "Can't Make Comment, Permission Denied"
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    current = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    user = db.session.query(Users).filter_by(phone_num=phone_num).first()

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
        current_app.logger.info("<%s>评论课程<%s>成功, 评论内容：%s" % (phone_num, course_id, content))
    except Exception as e:
        msg = "用户<%s>评论 课程<%s>失败, error:%s" % (phone_num, course_id, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    comment_info['nickName'] = user.nickName
    comment_info['phone_num'] = phone_num
    comment_info['msg'] = "success"
    return jsonify(comment_info)


# 存储脑电数据
@addData.route("/save_waves/", methods=["POST"])
def save_waves():
    """存储脑电数据接口，post请求中携带的data为：
    phone_num:电话号。代表学生
    course_name：脑电数据的课程名
    data：脑电数据
    url: http://www.xiaochengxueeg.xyz:8888/save_waves
    :return 所增加脑电数据的详细信息
    """
    phone_num = request.values.get("phone_num")
    course_name = request.values.get("course_name")
    data = request.values.get("data")

    try:

        course = db.session.query(Courses).filter_by(name=course_name).first()
        course_entry = CoursesEntry.query.filter_by(phone_num=phone_num, course_id=course.id).first()
        user = Users.query.filter_by(phone_num=phone_num).first()
    except Exception as e:
        msg = "获取用户%s | 课程%s 的报名信息失败，error:%s" % (phone_num, course_name, str(e))
        current_app.logger.info(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)

    if not course:
        msg = "Can't Save Wave, Course %s Is Not Found" % course_name
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)
    if not course_entry:
        # 没有权限 status=201 msg=Can't Save Wave, Permission Denied
        msg = "Can't Save Wave, Permission Denied"
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)
    if not user:
        msg = "Can't Save Wave, You Have Not Login"
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=201)

    current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    wave_info = {
        "user_id": user.id,
        "nickName": user.nickName,
        "username": course_entry.username,
        "phone_num": phone_num,

        "course_id": course.id,
        "course_name": course.name,
        "course_category": course.category,
        "course_avg_data": course.avg_data,
        "wave_data": data,
        "test_time": current
    }

    wave = Waves(**wave_info)
    db.session.add(wave)
    db.session.flush()

    # 查找课程对应的所有脑电数据, 修改脑电数据
    course_waves = course.waves.all()

    totle_data = 0
    for wave in course_waves:
        data = wave.data
        if data is None:
            data = 0
        # 遍历查询结果集的最后一个值为元组，原因不详
        elif isinstance(data, tuple):
            data = data[0]
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
        msg = "存储用户<%s> 的 <%s>课程 的脑电数据%s失败, error:%s" % (phone_num, course_name, data, str(e))
        current_app.logger.error(msg)
        return utils.make_resp(msg=json.dumps(msg), status=500)
    wave_info["msg"] = "success"
    return jsonify(wave_info)
