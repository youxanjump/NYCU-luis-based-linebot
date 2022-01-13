from bot_config import MSSQL_ENGINE_FLASK

from flask import Flask, request, render_template, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
import flask_admin.form as form
from flask_admin.contrib.sqla import ModelView


# Create flask app
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = MSSQL_ENGINE_FLASK
# hash hex string
app.config['SECRET_KEY'] = '9a44008af86bba94f5be62cf82fe9317'
app.debug = True


# Flask views
@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 帳號密碼直接定義在這
    users = {
        'testuser': {
            'password': 'testpassword',
            'permission': 1
        },
        'admin': {
            'password': 'admin',
            'permission': 3
        },
    }

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and password == users[username]['password']:
            session['logged_in'] = True
            session['permission'] = users[username]['permission']
            return redirect('/admin')
        else:
            return render_template('login/login.html', failed=True)

    return render_template('login/login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


db = SQLAlchemy(app)


# 不知道麼沒辦法設定id作為pk，也沒辦法讓他自動填入值
# 可以讓priary_key顯示出來的ModelView(可以編輯資料的頁面模板)
class AdminView(ModelView):
    def __init__(self, model, session, **kwargs):
        # 取得table的column的名字
        self.column_list = [c.key for c in model.__table__.columns]
        # print(self.column_list)
        # 將這些名字都顯示在View
        self.form_columns = self.column_list
        print(self.column_list)
        super(AdminView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        if 'logged_in' in session:
            # 針對不同分頁的權限設置
            if str(request.url_rule) == '/admin/consultantadmin/':
                if session['permission'] == 3:
                    return True
                else:
                    return abort(403)
            else:
                return True
        else:
            return redirect('/login')


# 學生餐廳相關的View
class RestaurantView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學生餐廳', '餐廳名稱')
    column_default_sort = '校區'


class RestaurantAdmin(db.Model):
    __tablename__ = '學生餐廳資訊'
    校區 = db.Column(db.String(10))
    學生餐廳 = db.Column(db.String(15))
    餐廳名稱 = db.Column(db.String(25),  primary_key=True)
    地點ID = db.Column(db.String(50))
    營業時間 = db.Column(db.TEXT)
    菜單網址 = db.Column(db.TEXT)

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
    學號起_06學年度 = db.Column(db.String(255))
    學號起_07學年度 = db.Column(db.String(255))
    學號起_08學年度 = db.Column(db.String(255))
    學號起_09學年度 = db.Column(db.String(255))
    學號起_10學年度 = db.Column(db.String(255))
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


# Information Table View
class InformationTableView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('Class', 'Information')
    column_default_sort = 'Class'


class InformationTableAdmin(db.Model):
    __tablename__ = 'information_table'
    Class = db.Column(db.String(20), primary_key=True)
    Information = db.Column(db.String(20), primary_key=True)
    Alias = db.Column(db.String(20), primary_key=True)

    def __unicode__(self):
        return self.desc


# 系所簡介以及功能
class IntroductionView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學院', '系所', '介紹類別')
    column_default_sort = '系所'


class IntroductionAdmin(db.Model):
    __tablename__ = '各單位簡介或功能'
    校區 = db.Column(db.String(10))
    學院 = db.Column(db.String(10))
    系所 = db.Column(db.String(20),  primary_key=True)
    學歷 = db.Column(db.String(10),  primary_key=True)
    組別 = db.Column(db.String(20),  primary_key=True)
    介紹類別 = db.Column(db.String(20),  primary_key=True)
    介紹內容 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 系所申請與轉換
class AcademyAdmissionView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學院', '系所')
    column_default_sort = '系所'


class AcademyAdmissionAdmin(db.Model):
    __tablename__ = '系所申請與轉換'
    校區 = db.Column(db.String(10))
    學院 = db.Column(db.String(10))
    系所 = db.Column(db.String(20),  primary_key=True)
    學歷 = db.Column(db.String(10),  primary_key=True)
    五年碩申請 = db.Column(db.TEXT)
    輔系申請 = db.Column(db.TEXT)
    雙主修申請 = db.Column(db.TEXT)
    雙聯學位申請 = db.Column(db.TEXT)
    轉入系所 = db.Column(db.TEXT)
    轉出系所 = db.Column(db.TEXT)
    入學方式 = db.Column(db.TEXT)
    逕博相關規定 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 系所簡介以及功能
class GraguationView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學院', '系所', '畢業相關項目')
    column_default_sort = '系所'


class GraguationAdmin(db.Model):
    __tablename__ = '系所畢業規定'
    校區 = db.Column(db.String(10))
    學院 = db.Column(db.String(10))
    系所 = db.Column(db.String(20),  primary_key=True)
    學歷 = db.Column(db.String(10),  primary_key=True)
    組別 = db.Column(db.String(20),  primary_key=True)
    畢業相關項目 = db.Column(db.String(20),  primary_key=True)
    項目畢業規定 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 系所申請與轉換
class CourseView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學院', '系所')
    column_default_sort = '系所'


class CourseAdmin(db.Model):
    __tablename__ = '系所課程相關'
    校區 = db.Column(db.String(10))
    學院 = db.Column(db.String(10))
    系所 = db.Column(db.String(20),  primary_key=True)
    學歷 = db.Column(db.String(10),  primary_key=True)
    課程免修 = db.Column(db.TEXT)
    課程免擋修 = db.Column(db.TEXT)
    考古題相關 = db.Column(db.TEXT)
    課程種類一覽 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 場地物品租借
class PlaceObjectBorrowView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '大樓名稱', '場地或設備名稱')
    column_default_sort = '大樓名稱'


class PlaceObjectBorrowAdmin(db.Model):
    __tablename__ = '場地物品租借方式'
    校區 = db.Column(db.String(10),  primary_key=True)
    大樓名稱 = db.Column(db.String(10),  primary_key=True)
    場地或設備名稱 = db.Column(db.String(20),  primary_key=True)
    簡短資訊 = db.Column(db.TEXT)
    租借方式 = db.Column(db.TEXT)
    詳細資訊 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 答案回饋
class AnswerFeedbackView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('ID', 'Question', 'Feedback')
    column_default_sort = 'Time'


class AnswerFeedbackAdmin(db.Model):
    __tablename__ = '答案回饋'
    ID = db.Column(db.TEXT,  primary_key=True)
    Time = db.Column(db.String(20),  primary_key=True)
    Question = db.Column(db.TEXT)
    Feedback = db.Column(db.String(20))

    def __unicode__(self):
        return self.desc


# 圖書館借還書規定
class LibraryView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '行為')
    column_default_sort = '校區'


class LibraryAdmin(db.Model):
    __tablename__ = '圖書館借還書'
    校區 = db.Column(db.String(10),  primary_key=True)
    行為 = db.Column(db.String(20),  primary_key=True)
    行為細項 = db.Column(db.String(20))
    方式 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 獎助學金申請方式
class ScholarshipView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('種類', '校區', '學院', '系所')
    column_default_sort = '學院'


class ScholarshipAdmin(db.Model):
    __tablename__ = '獎助學金申請方式'
    種類 = db.Column(db.String(10))
    校區 = db.Column(db.String(20),  primary_key=True)
    學院 = db.Column(db.String(20))
    系所 = db.Column(db.String(20),  primary_key=True)
    申請方式 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 學分抵免與認定之規定
class CreditsView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('校區', '學院', '系所', '學分問題類別')
    column_default_sort = '系所'


class CreditsAdmin(db.Model):
    __tablename__ = '學分抵免與認定之規定'
    校區 = db.Column(db.String(10))
    學院 = db.Column(db.String(10))
    系所 = db.Column(db.String(20),  primary_key=True)
    學歷 = db.Column(db.String(10),  primary_key=True)
    組別 = db.Column(db.String(20),  primary_key=True)
    學分問題類別 = db.Column(db.String(20),  primary_key=True)
    學分規定 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# 學校各部門連絡方式
class ContactView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('學校', '單位類別', '單位', '部門')
    column_default_sort = '優先度'


class ContactAdmin(db.Model):
    __tablename__ = '學校各部門連絡方式'
    學校 = db.Column(db.String(10))
    單位類別 = db.Column(db.String(10))
    單位 = db.Column(db.String(20),  primary_key=True)
    優先度 = db.Column(db.String(10))
    部門 = db.Column(db.String(20),  primary_key=True)
    分機 = db.Column(db.String(20))
    專線 = db.Column(db.String(20))
    位置 = db.Column(db.TEXT)
    網站 = db.Column(db.String(50))
    updatatime = db.Column(db.String(20))
    source = db.Column(db.String(50))
    經度 = db.Column(db.String(20))
    緯度 = db.Column(db.String(20))
    開放時間 = db.Column(db.TEXT)

    def __unicode__(self):
        return self.desc


# Interview Table View
class InterviewTableView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('Question', 'Answer')
    column_default_sort = 'Question'


class InterviewTableAdmin(db.Model):
    __tablename__ = 'interview_information'
    Question = db.Column(db.String(50), primary_key=True)
    Answer = db.Column(db.Text)

    def __unicode__(self):
        return self.desc


# Mapping Intent Table View
class MappingIntentView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('Intent', 'Answer')
    column_default_sort = 'Intent'


class MappingIntentAdmin(db.Model):
    __tablename__ = 'mapping_intent'
    Intent = db.Column(db.String(50), primary_key=True)
    Answer = db.Column(db.Text)

    def __unicode__(self):
        return self.desc


# AED Table View
class AEDView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('緯度', '經度')
    column_default_sort = '校區'


class AEDAdmin(db.Model):
    __tablename__ = '校園AED'
    校區 = db.Column(db.Text)
    地點描述 = db.Column(db.Text)
    緯度 = db.Column(db.Text,  primary_key=True)
    經度 = db.Column(db.Text,  primary_key=True)

    def __unicode__(self):
        return self.desc


# ATM Table View
class ATMView(AdminView):
    # column_searchable_list不能只放一個PK(待查證原因)
    column_searchable_list = ('緯度', '經度')
    column_default_sort = '校區'


class ATMAdmin(db.Model):
    __tablename__ = '校園ATM'
    校區 = db.Column(db.Text)
    銀行名稱 = db.Column(db.Text)
    地點描述 = db.Column(db.Text)
    緯度 = db.Column(db.Text,  primary_key=True)
    經度 = db.Column(db.Text,  primary_key=True)

    def __unicode__(self):
        return self.desc


# Create admin interface
admin = admin.Admin(name="《陽明交大校園聊天機器人》後台管理系統", template_mode='bootstrap4')
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
admin.add_view(InformationTableView(
                    InformationTableAdmin,
                    db.session,
                    name='實體別稱表',
                    category='小幫手相關'
                ))
admin.add_view(IntroductionView(
                    IntroductionAdmin,
                    db.session,
                    name='各單位簡介或功能',
                    category='小幫手相關'
                ))

admin.add_view(AcademyAdmissionView(
                    AcademyAdmissionAdmin,
                    db.session,
                    name='系所申請與轉換',
                    category='小幫手相關'
                ))
admin.add_view(GraguationView(
                    GraguationAdmin,
                    db.session,
                    name='系所畢業規定',
                    category='小幫手相關'
                ))
admin.add_view(CourseView(
                    CourseAdmin,
                    db.session,
                    name='系所課程相關',
                    category='小幫手相關'
                ))
admin.add_view(PlaceObjectBorrowView(
                    PlaceObjectBorrowAdmin,
                    db.session,
                    name='場地物品租借方式',
                    category='小幫手相關'
                ))
admin.add_view(AnswerFeedbackView(
                    AnswerFeedbackAdmin,
                    db.session,
                    name='問題回饋',
                    category='小幫手相關'
                ))
admin.add_view(LibraryView(
                    LibraryAdmin,
                    db.session,
                    name='圖書館借還書規定',
                    category='小幫手相關'
                ))
admin.add_view(ScholarshipView(
                    ScholarshipAdmin,
                    db.session,
                    name='獎助學金申請方式',
                    category='小幫手相關'
                ))
admin.add_view(CreditsView(
                    CreditsAdmin,
                    db.session,
                    name='學分抵免與認定之規定',
                    category='小幫手相關'
                ))
admin.add_view(ContactView(
                    ContactAdmin,
                    db.session,
                    name='學校各部門連絡方式',
                    category='小幫手相關'
                ))
admin.add_view(InterviewTableView(
                    InterviewTableAdmin,
                    db.session,
                    name='其他訪談資訊',
                    category='小幫手相關'
                ))
admin.add_view(MappingIntentView(
                    MappingIntentAdmin,
                    db.session,
                    name='自然語言與按鈕對應表',
                    category='小幫手相關'
                ))
admin.add_view(AEDView(
                    AEDAdmin,
                    db.session,
                    name='校園AED資訊',
                    category='小幫手相關'
                ))
admin.add_view(ATMView(
                    ATMAdmin,
                    db.session,
                    name='校園ATM資訊',
                    category='小幫手相關'
                ))
admin.init_app(app)

if __name__ == '__main__':

    # Start app
    app.run(port=5566)
