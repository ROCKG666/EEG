from flask import request, current_app, jsonify, json
from app.models import *
from app import utils
from . import getData


# 获取所有评论内容
@getData.route("/get_comments")
def get_comments():
    """选择性进行查询评论,不传参数查询所有用户所有课程的评论，
    可以通过nickName和course_id 限制所查询的结果
    url: http://39.108.166.132:8888/get_comments?nickName=xxx&course_id=xxx
    :return 评论的列表，所有学生的所有评论
    """
    current_app.logger.info("get all comments info")
    nickName = request.values.get("nickName")
    course_id = request.values.get("course_id")
    comment_list = list()
    # 查询所有评论
    if nickName is None and course_id is None:
        comments = Comments.query.all()
        for comment in comments:
            user_id = comment.user_id
            user = Users.query.filter_by(id=user_id).first()
            course_id = comment.course_id
            course = Courses.query.filter_by(id=course_id).first()
            comment_info = {
                "id": comment.id,
                "content": comment.content,
                "user_id": user_id,
                "nickName": user.nickName,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "comment_time": comment.comment_time,
                "photo": user.photo
            }
            comment_list.append(comment_info)
        current_app.logger.info("get all comments ok, data-->%s" % comment_list)

    # 用户名存在 课程为空
    elif nickName and course_id is None:
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        if not user:
            errmsg = "用户%s不存在" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp
        comments = db.session.query(Comments).filter_by(user_id=user.id).all()
        comment_list = list()
        for comment in comments:
            course_id = comment.course_id
            course = Courses.query.filter_by(id=course_id).first()
            comment_info = {
                "id": comment.id,
                "content": comment.content,
                "user_id": user.id,
                "nickName": nickName,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "comment_time": comment.comment_time,
                "photo": user.photo
            }
            comment_list.append(comment_info)
        current_app.logger.info("get comments of user <%s> ok, data-->%s" % (nickName, comment_list))

    # 课程存在 用户名为空
    elif nickName is None and course_id:
        course = db.session.query(Courses).filter_by(id=course_id).first()
        if not course:
            errmsg = "课程%s不存在" % course_id
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp
        comments = db.session.query(Comments).filter_by(course_id=course_id).all()
        for comment in comments:
            user_id = comment.user_id
            user = Users.query.filter_by(id=user_id).first()
            comment_info = {
                "id": comment.id,
                "content": comment.content,
                "user_id": user_id,
                "nickName": user.nickName,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "comment_time": comment.comment_time,
                "photo": user.photo
            }
            comment_list.append(comment_info)
        current_app.logger.info("get comments of course <%s> ok, data-->%s" % (course_id, comment_list))

    # 课程存在 用户名存在
    elif nickName and course_id:
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        if not user:
            errmsg = "用户%s不存在" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        course = db.session.query(Courses).filter_by(id=course_id).first()
        if not course:
            errmsg = "课程%s不存在" % course_id
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        comments = db.session.query(Comments).filter_by(user_id=user.id, course_id=course_id).all()
        for comment in comments:
            comment_info = {
                "id": comment.id,
                "content": comment.content,
                "user_id": user.id,
                "nickName": nickName,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "comment_time": comment.comment_time,
                "photo": user.photo
            }
            comment_list.append(comment_info)

        current_app.logger.info("get comments of <%s> ok, data-->%s" % (nickName, comment_list))
    return jsonify(comment_list)


# 获取脑电数据
@getData.route("/get_waves")
def get_waves():
    """选择性进行查询脑电数据
    http://39.108.166.132:8888/get_waves?nickName=xxx&course_id=xxx
    :return 脑电数据的列表
    """
    current_app.logger.info("get waves info")
    nickName = request.values.get("nickName")
    course_id = request.values.get("course_id")
    data_list = list()

    if nickName and course_id:
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        if not user:
            errmsg = "用户%s不存在, 请核对" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        course = db.session.query(Courses).filter_by(id=course_id).first()
        if not course:
            errmsg = "课程%s不存在, 请核对" % course_id
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp
        wave = Waves.query.filter_by(user_id=user.id, course_id=course_id).first()
        if not wave:
            errmsg = "学生%s + 课程%s 的脑电数据不存在, 请核对" % (nickName, course_id)
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        wave_info = {
            "id": wave.id,
            "data": wave.data,
            "test_time": wave.test_time,
            "user_id": user.id,
            "nickName": nickName,
            "photo": user.photo,
            "course_id": course_id,
            "course_name": course.name,
            "course_category": course.category,
            "course_avg_data": course.avg_data,
        }
        current_app.logger.info("get waves of student<%s> + course<%s> ok, data-->%s" % (nickName, course_id, data_list))
        data_list.append(wave_info)

    elif nickName and not course_id:
        user = db.session.query(Users).filter_by(nickName=nickName).first()
        if not user:
            errmsg = "用户%s不存在, 请核对" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp
        waves = user.waves
        if not waves:
            errmsg = "学生%s 的脑电数据不存在, 请核对" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        for wave in waves:
            course_id = wave.course_id
            course = db.session.query(Courses).filter_by(id=course_id).first()
            wave_info = {
                "id": wave.id,
                "data": wave.data,
                "test_time": wave.test_time,
                "user_id": user.id,
                "nickName": nickName,
                "photo": user.photo,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "course_avg_data": course.avg_data,
            }
            current_app.logger.info("get  waves of student<%s> ok, data-->%s" % (nickName, data_list))
            data_list.append(wave_info)

    elif not nickName and course_id:
        course = db.session.query(Courses).filter_by(id=course_id).first()
        if not course:
            errmsg = "课程%s不存在, 请核对" % course_id
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        waves = course.waves
        if not waves:
            errmsg = "课程%s 的脑电数据不存在, 请核对" % nickName
            resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
            return resp

        for wave in waves:
            user_id = wave.user_id
            user = db.session.query(Users).filter_by(id=user_id).first()

            wave_info = {
                "id": wave.id,
                "data": wave.data,
                "test_time": wave.test_time,
                "user_id": user_id,
                "nickName": user.nickName,
                "photo": user.photo,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "course_avg_data": course.avg_data,
            }
            current_app.logger.info("get  waves of course<%s> ok, data-->%s" % (nickName, data_list))
            data_list.append(wave_info)

    else:
        waves = Waves.query.all()
        for wave in waves:
            course_id = wave.course_id
            course = db.session.query(Courses).filter_by(id=course_id).first()

            user_id = wave.user_id
            user = db.session.query(Users).filter_by(id=user_id).first()

            wave_info = {
                "id": wave.id,
                "data": wave.data,
                "test_time": wave.test_time,
                "user_id": wave.user_id,
                "nickName": user.nickName,
                "photo": user.photo,
                "course_id": course_id,
                "course_name": course.name,
                "course_category": course.category,
                "course_avg_data": course.avg_data,
            }
            current_app.logger.info("get all waves ok, data-->%s" % data_list)
            data_list.append(wave_info)
    # return jsonify(data_list)
    return jsonify(data_list)


@getData.route("/get_user_info")
def get_user_info():
    """获取用户信息，get请求中参数携带nickName + user_type
    此接口中角色必须绑定了微信名才可查询
    url: http://39.108.166.132:8888/get_user_info? nickName=xxx & user_type=xxx
    :return 查询到的用户信息, 如果没信息则时空列表
    """
    current_app.logger.info("get user info")
    nickName = request.values.get("nickName")
    user_type = request.values.get("user_type")
    user = db.session.query(Users).filter_by(nickName=nickName, user_type=user_type).first()
    if not user:
        errmsg = "用户%s不存在" % nickName
        resp = utils.make_resp(msg=json.dumps(errmsg), status=201)
        return resp

    user_info = {
        "nickName": nickName,
        "user_type": user_type,
        "phone_num": user.phone_num,
        "intro": user.intro,
        'photo': user.photo
    }

    if user_type == "students":
        # user_info["waves"] = user.students.waves
        pass
    elif user_type == "teachers":
        # user_info["courses"] = user.teachers.courses
        user_info["school_id"] = user.teacher.school_id
    else:
        user_info["principal"] = user.school.principal
        user_info["building"] = user.school.building

    current_app.logger.info("get <%s>'s info ok, data-->%s" % (nickName, user_info))
    return jsonify(user_info)


@getData.route("/get_schools")
def get_schools():
    schools = db.session.query(Schools).all()
    schools_list = list()
    for school in schools:
        schools_info = {
            "id": school.id,
            "name": school.name,
            "intro": school.intro,
            'photo': school.photo,
            "principal": school.principal,
            "building": school.building,
        }
        schools_list.append(schools_info)
    current_app.logger.info("get all schools ok, data-->%s" % schools_list)
    return jsonify(schools_list)


@getData.route("/get_teachers")
def get_teachers():
    teachers = db.session.query(Teachers).all()
    teachers_list = list()

    for teacher in teachers:
        school_id = teacher.school_id
        school = db.session.query(Schools).filter_by(id=school_id).first()
        teacher_info = {
            "id": teacher.id,
            "name": teacher.name,
            "intro": teacher.intro,
            "photo": teacher.photo,
            "course_name": teacher.course.name,
            "course_category": teacher.course.category,
            "school_id": school_id,
            "school_name": school.name,
        }
        teachers_list.append(teacher_info)
    current_app.logger.info("get all teachers ok, data-->%s" % teachers_list)
    return jsonify(teachers_list)


@getData.route("/get_courses")
def get_courses():
    courses = db.session.query(Courses).all()
    courses_list = list()

    for course in courses:
        teacher_id = course.teacher_id
        teacher = db.session.query(Teachers).filter_by(id=teacher_id).first()
        courses_info = {
            "id": course.id,
            "name": course.name,
            "avg_data": course.avg_data,
            "category": course.category,
            "content_url": course.content_url,
            "teacher": teacher.name,
            "teacher_id": teacher_id,
        }
        courses_list.append(courses_info)
    current_app.logger.info("get all courses ok, data-->%s" % courses_list)
    return jsonify(courses_list)
