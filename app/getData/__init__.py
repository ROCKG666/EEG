from flask import Blueprint
"""此应用主要负责获取数据功能"""

getData = Blueprint("getData", __name__)
# 导入视图程序包，声明再那个视图中可以使用此蓝图，如果不导入将无法注册路由
# 视图程序包必须在创建蓝图之后导入！！！
from . import views
