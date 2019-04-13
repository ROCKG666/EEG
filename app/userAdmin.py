#from cronlog import unicode
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired
from .models import *


class UsersForm(FlaskForm):
    # Flask-Admin是不提供主键修改的表单的, 可以自定义需要修改的字段
    # id = IntegerField()
    nickName = StringField(label='微信名')
    phone_num = StringField(label='电话号')
    password = StringField(label='报名密码')
    photo = StringField(label='头像')
    # user_type = SelectField(label='用户类型',
    #                         validators=[DataRequired('请选择标签')],
    #                         choices=[('students', '学生'), ('teachers', '老师'), ('schools', '机构')],
    #                         coerce=str # 解决表单的Not a valid choice
    #                         )
    #


class UsersModelView(ModelView):
    """用户的后台展示视图"""
    # 显示主键-->id
    column_display_pk = True
    column_create_pk = True
    form = UsersForm


admin = Admin(name="脑电小程序", template_mode='bootstrap3')
admin.add_view(UsersModelView(Users, db.session, name="学生管理"))
admin.add_view(ModelView(Schools, db.session, name="学校管理"))
admin.add_view(ModelView(Teachers, db.session, name="老师管理"))
admin.add_view(ModelView(Courses, db.session, name="课程管理"))
admin.add_view(ModelView(Comments, db.session, name="评论管理"))
admin.add_view(ModelView(Waves, db.session, name="脑电数据"))
admin.add_view(ModelView(CoursesEntry, db.session, name="报名课程"))
