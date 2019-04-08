# -*- coding:utf8 -*-
"""存储这整个项目需要的方法"""
import datetime
import logging
import sys
from flask import make_response


def get_image_path(filename, user_type):
    """
    根据用户类型选择图片的存储路径
    :param filename: 文件名
    :param user_type: 用户类型
    :return: 存储路径 --> app/static/upload/students/Y-m-d-H-M-S-f.png
    """
    # 以年-月-日-时-分-秒-6位浮点数 的格式生成当前时间
    current = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    # 获取文件后缀名
    suffix = filename.split(".")[-1]
    # 使用当前时间+后缀名生成图片名
    filename = current + '.' + suffix
    # 声明图片的保存路径
    upload_path = 'app/static/upload/' + user_type + '/' + filename
    return upload_path


def make_resp(msg, status):
    resp = make_response(msg)
    resp.status = str(status)
    resp.headers["content-type"] = 'application/json; charset=UTF-8'
    return resp


# 设置日志的格式
def set_log(app):
    format_str = '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    logging_formatter = logging.Formatter(format_str)
    fileHd = logging.FileHandler('flask.log', encoding='UTF-8')
    fileHd.setLevel(logging.DEBUG)
    fileHd.setFormatter(logging_formatter)

    consoleFd = logging.StreamHandler(sys.stdout)
    consoleFd.setLevel(logging.DEBUG)
    consoleFd.setFormatter(logging_formatter)
    # 日志记录到文件
    app.logger.addHandler(fileHd)
    # 日志输出到打印台
    app.logger.addHandler(consoleFd)
