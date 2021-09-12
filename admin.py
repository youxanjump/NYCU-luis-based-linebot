from bot_config import MSSQL_ENGINE_FLASK

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
import flask_admin.form as form
from flask_admin.contrib.sqla import ModelView


# Create flask app
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = MSSQL_ENGINE_FLASK
app.config['SECRET_KEY'] = 'dumb_screct'
app.debug = True
db = SQLAlchemy(app)


# 不知道麼沒辦法設定id作為pk，野蠻辦法讓他自動填入值
# 可以讓priary_key顯示出來
class AdminView(ModelView):
    def __init__(self, model, *args, **kwargs):
        # 取得table的column的名字
        self.column_list = [c.key for c in model.__table__.columns]
        # 將這些名字都顯示在View
        self.form_columns = self.column_list
        super(AdminView, self).__init__(model, *args, **kwargs)


class RestaurantView(AdminView):
    column_searchable_list = ('校區', '學生餐廳', '餐廳名稱')


class RestaurantAdmin(db.Model):
    __tablename__ = '學生餐廳資訊'
    校區 = db.Column(db.String(10))
    學生餐廳 = db.Column(db.String(15))
    餐廳名稱 = db.Column(db.String(10),  primary_key=True)
    地點ID = db.Column(db.String(50))
    營業時間 = db.Column(db.TEXT)
    菜單網址 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# Flask views
@app.route('/')
def index():
    return '<a class="btn btn-primary" href="/admin"><i class="glyphicon glyphicon-chevron-left"></i>進入後台管理系統</a>'


# Create admin interface
admin = admin.Admin(name="《陽明交大 - 校園小幫手》後台管理系統", template_mode='bootstrap4')
admin.add_view(RestaurantView(
                    RestaurantAdmin,
                    db.session,
                    name='學生餐廳資訊',
                    category='請選擇欲更新的資訊'
                ))
admin.init_app(app)

if __name__ == '__main__':

    # Start app
    app.run(port=5566)
