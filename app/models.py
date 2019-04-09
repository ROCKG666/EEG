# -*- coding=utf-8 -*-
from .exts import db
from flask_login import UserMixin


courses_users = db.Table(
    "courses_users",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)


# 用户模型类--针对学生
class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickName = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    photo = db.Column(db.String(500)) # 暂时保留photo字段

    comments = db.relationship("Comments", backref='user', lazy='dynamic')
    waves = db.relationship("Waves", backref='user', lazy='dynamic')

    # Users类中通过db.relationship定义了和Courses类之间的关系，它们之间连接的桥梁就是courses_users，
    # courses_users定义了两张关联表之间主键的对应关系。Users对象含有courses集合属性，代表课程的集合，
    # 而通过backref动态地给Courses对象增加了user属性，代表本课程所对应的学生有哪些。
    courses = db.relationship(
        "Courses",
        secondary=courses_users,
        lazy="dynamic",
        backref=db.backref("users", lazy="dynamic"),
        cascade='all, delete',  # 设置级联删除
        passive_deletes=True
    )

    def __init__(self, **kwargs):
        self.nickName = kwargs.get("nickName")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.photo = kwargs.get("photo")

    def to_dict(self):
        user_info = {
            "id": self.id,
            "nickName": self.nickName,
            "username": self.username,
        }
        return user_info

    def __repr__(self):
        return self.nickName

    # 可以重写UserMixin 的四个方法

    # 密码加密：
    # @property
    # def password(self):
    #     return self._password
    #     # raise AttributeError(u'文明密码不可读')

    # @password.setter
    # def password(self, rawpwd):
    #     self._password = generate_password_hash(rawpwd)

    # # 定义一个验证密码的方法
    # def check_password(self, rawpwd):
    #     return check_password_hash(self.password, rawpwd)


class Schools (db.Model):
    __tablename__ = "schools"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    principal = db.Column(db.String(50))
    building = db.Column(db.String(100))
    photo = db.Column(db.String(100))
    intro = db.Column(db.String(300))

    # Teachers类中增加隐式属性school,反向引用schools表,该属性可代替teacher_id来访问Teachers模型,得到模型对象
    # Schools类通过relationship关联到Teachers类，给自己定义了teachers集合属性，代表本校下的所有老师。
    # db.relationship关联到Teachers类，通过backref动态地给Teachers类增加了school属性，代表Teacher所属的学校。
    teachers = db.relationship("Teachers",
                               backref="school",
                               lazy="dynamic",
                               cascade='all, delete-orphan',
                               passive_deletes=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.principal = kwargs.get("principal")
        self.building = kwargs.get("building")
        self.photo = kwargs.get("photo")
        self.intro = kwargs.get("intro")

    # def __repr__(self):
    #     return self.name


class Teachers(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    photo = db.Column(db.String(100))
    intro = db.Column(db.String(300))
    # 一名老师对应一门课程， 反向引用到Courses类，并增加course属性，代表这个老师的所有课程
    course = db.relationship("Courses", backref="teacher", uselist=False)

    # 学校和老师一对多，Teachers对象具有隐式属性school, 代表这个老师的学校
    # 设置级联删除，删除schools表中的数据时，teachers表中引用schools表的数据也自动删除
    # 如果不设置级联删除，必须先删除teachers表中引用schools表中数据，才能删除schools表中的数据
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id", ondelete='CASCADE'))

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.photo = kwargs.get("photo")
        self.intro = kwargs.get("intro")

    def __repr__(self):
        return self.name


class Courses(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    avg_data = db.Column(db.Float)
    category = db.Column(db.Enum("listening", "reading", "writing", "speaking"))
    content_url = db.Column(db.String(100))

    # Courses对象具有teacher属性，代表其所属的老师
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))

    comments = db.relationship("Comments", backref='course', lazy='dynamic')
    waves = db.relationship("Waves", backref='course', lazy='dynamic')

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.avg_data = kwargs.get("avg_data")
        self.category = kwargs.get("category")
        self.teacher_id = kwargs.get("teacher_id")
        self.content_url = kwargs.get("content_url")

    def __repr__(self):
        return self.name


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    # Comments对象具有user和course属性，代表其所属的学生和课程
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    content = db.Column(db.String(300))
    comment_time = db.Column(db.String(100))

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.course_id = kwargs.get("course_id")
        self.content = kwargs.get("content")
        self.comment_time = kwargs.get("comment_time")

    def __repr__(self):
        return str(self.id)

class Waves(db.Model):
    __tablename__ = "waves"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Waves对象分别具有user和course属性，代表其所属的学生和课程
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    data = db.Column(db.Float)
    test_time = db.Column(db.String(100))

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.course_id = kwargs.get("course_id")
        self.data = kwargs.get("wave_data")
        self.test_time = kwargs.get("test_time")

    def __repr__(self):
        # return self.data
        # __str__ returned non - string (type float)
        return str(self.data)

# db.drop_all()
#########################################


