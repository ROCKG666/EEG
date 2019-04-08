# -*- coding=utf-8 -*-
"""整体项目的管理模块"""
from app import create_app


# 创建flask应用
app = create_app()


if __name__ == "__main__":
    # 运行flask应用（服务）
    app.run(host='0.0.0.0', port=8888)
