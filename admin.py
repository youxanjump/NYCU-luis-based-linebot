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


# 不知道麼沒辦法設定id作為pk，也沒辦法讓他自動填入值
# 可以讓priary_key顯示出來的View
class AdminView(ModelView):
    def __init__(self, model, session, **kwargs):
        # 取得table的column的名字
        self.column_list = [c.key for c in model.__table__.columns]
        # print(self.column_list)
        # 將這些名字都顯示在View
        self.form_columns = self.column_list
        print(self.column_list)
        super(AdminView, self).__init__(model, session, **kwargs)


# 學生餐廳相關的View
class RestaurantView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學生餐廳', '餐廳名稱')
    column_default_sort = '校區'


class RestaurantAdmin(db.Model):
    __tablename__ = '學生餐廳資訊'
    校區 = db.Column(db.String(10))
    學生餐廳 = db.Column(db.String(15))
    餐廳名稱 = db.Column(db.String(10),  primary_key=True)
    地點ID = db.Column(db.String(50))
    營業時間 = db.Column(db.TEXT)
    菜單網址 = db.Column(db.String(50))

    def __unicode__(self):
        return self.desc


# 諮商師對應資訊相關的View
class ConsultantView(AdminView):
    column_searchable_list = ('系所', '諮商師')
    column_default_sort = '諮商師'


class ConsultantAdmin(db.Model):
    __tablename__ = '學號_系所_諮商師 對應表'
    院 = db.Column(db.String(255))
    系所 = db.Column(db.String(255), primary_key=True)
    # 學號_06 = db.Column("06學號起", db.String(255))
    # 學號_07 = db.Column("07學號起", db.String(255))
    # 學號_08 = db.Column("08學號起", db.String(255))
    # 學號_09 = db.Column("09學號起", db.String(255))
    諮商師 = db.Column(db.String(255))
    分機 = db.Column(db.Integer)
    email = db.Column(db.String(255))

    def __unicode__(self):
        return self.desc


# Repair Table View
class RepairTableView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('Intent', 'Repair')
    column_default_sort = 'Intent'


class RepairTableAdmin(db.Model):
    __tablename__ = 'repair_table'
    Intent = db.Column(db.String(20), primary_key=True)
    Repair = db.Column(db.Text)

    def __unicode__(self):
        return self.desc


# Flask views
@app.route('/')
def index():
    # print(db.engine.table_names())
    testadmin = ConsultantAdmin()
    print(testadmin.__table__.columns.keys())
    return '<a class="btn btn-primary" href="/admin"><i class="glyphicon glyphicon-chevron-left"></i>進入後台管理系統</a>'


# Create admin interface
admin = admin.Admin(name="《陽明交大 - 校園小幫手》後台管理系統", template_mode='bootstrap4')
admin.add_view(RestaurantView(
                    RestaurantAdmin,
                    db.session,
                    name='學生餐廳資訊',
                    category='小幫手相關'
                ))
admin.add_view(ConsultantView(
                    ConsultantAdmin,
                    db.session,
                    name='諮商師與學號對應表',
                    category='諮心好友相關'
                ))
admin.add_view(RepairTableView(
                    RepairTableAdmin,
                    db.session,
                    name='對話修補機制',
                    category='小幫手相關'
                ))
admin.init_app(app)

if __name__ == '__main__':

    # Start app
    app.run(port=5566)
