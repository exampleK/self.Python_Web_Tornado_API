"""
小学招生-学生家长接口
"""
from sitebase.base import BaseHandler, login_required
from sitebase.models import PrimaryStudents, \
    Primary_plan, Family, School, CheckRecord, Account
from sitebase.utils import sa_r2d, sa_rs2ds
import datetime


class PrimaryStudentInfoHandler(BaseHandler):
    """
    小学学生信息
    /primaryStudent/info
    """
    @login_required([0, 1, 3])
    def post(self):
        id = self.get_argument("id", '')
        udata = self.db.query(PrimaryStudents).get(id)
        if not udata:
            self.write({'code': 'error'})
            return
        # enroll_uid = udata.uid
        # # 判断user是否是这个学生的填报人
        # if enroll_uid != self.user_id:
        #     # 也有可能是学校或教育局添加
        #     account = self.db.query(Account).filter(
        #         Account.uid == enroll_uid
        #     ).first()
        #     if not account or account.role != 3:
        #         self.write({'code': 1402})
        #         return
        school = self.db.query(School).get(udata.school_id)
        role = self.current_user['role']
        org_id = self.current_user['org_id']
        # 其他学校无权限
        if role == 1 and org_id != udata.school_id:
            self.write({'code': 1402})
            return
        family = self.db.query(Family).filter(
            Family.uid == id,
            Family.tag == 0
        ).all()
        # 查询这个学生的审核记录
        records = self.db.query(CheckRecord).filter(
            CheckRecord.tag == 1,
            CheckRecord.student_id == id
        ).all()
        self.write({
            'code': 'ok',
            'result': sa_r2d(udata),
            'family': sa_rs2ds(family),
            'school': sa_r2d(school),
            'remarks': sa_rs2ds(records)
        })


class EnrollFirstHandler(BaseHandler):
    """
    小学预报名第一个页面保存
    /primaryStudent/enroll/first
    """
    @login_required([0])
    def post(self):
        uid = self.user_id
        id_card = self.get_argument("id_card", '')
        '''
        id_card将字符串中字符转换成大写
        '''
        id_card = id_card.upper()
        '''
        验证接收数据
        '''
        exist = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id_card == id_card,
            PrimaryStudents.uid != uid,
            PrimaryStudents.year == datetime.datetime.now().strftime('%Y')
        ).first()
        if exist:
            self.write({'code': 'error', 'tag': 4, 'msg': '身份证已经被填报'})
            return
        school_id = self.get_argument("school_id", '')
        fullname = self.get_argument("fullname", '')
        gender = self.get_argument("gender", '')
        nationality = self.get_argument("nationality", '')
        native_place = self.get_argument("native_place", '')
        ethnic = self.get_argument("ethnic", '')
        birthdate = self.get_argument("birthdate", '')
        is_gat = self.get_argument("is_gat", '')
        heath = self.get_argument("heath", '')
        yfjzz = self.get_argument("yfjzz", '')
        kindergarten = self.get_argument("kindergarten", '')
        birth_id = self.get_argument("birth_id", '')
        avatar = self.get_argument("avatar", '')
        leg_address = self.get_argument("leg_address", '')
        chanqun = self.get_argument("chanqun", '')
        fcz_id = self.get_argument("fcz_id", '')
        fcz_number = self.get_argument("fcz_number", '')
        fcz_picture = self.get_argument("fcz_picture", '')
        zufang_picture = self.get_argument("zufang_picture", '')

        baseinfo = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id_card == id_card,
            PrimaryStudents.uid == uid,
            Primary_plan.status == 0
        ).first()
        # 如果身份证存在则修改新表
        if baseinfo:
            baseinfo.school_id = school_id
            baseinfo.fullname = fullname
            baseinfo.id_card = id_card
            baseinfo.gender = gender
            baseinfo.nationality = nationality
            baseinfo.native_place = native_place
            baseinfo.ethnic = ethnic
            baseinfo.birthdate = birthdate
            baseinfo.is_gat = is_gat
            baseinfo.heath = heath
            baseinfo.yfjzz = yfjzz
            baseinfo.kindergarten = kindergarten
            baseinfo.birth_id = birth_id
            baseinfo.avatar = avatar
            baseinfo.leg_address = leg_address
            baseinfo.chanqun = chanqun
            baseinfo.fcz_id = fcz_id
            baseinfo.fcz_number = fcz_number
            baseinfo.fcz_picture = fcz_picture
            baseinfo.zufang_picture = zufang_picture

            self.db.commit()
            self.write({
                'code': 'ok',
                'result': baseinfo.id
            })
        # 如果不存在则创建新表
        else:
            baseinfo = PrimaryStudents(
                school_id=school_id,
                uid=uid,
                fullname=fullname,
                id_card=id_card,
                gender=gender,
                nationality=nationality,
                native_place=native_place,
                ethnic=ethnic,
                birthdate=birthdate,
                is_gat=is_gat,
                heath=heath,
                yfjzz=yfjzz,
                kindergarten=kindergarten,
                birth_id=birth_id,
                avatar=avatar,
                leg_address=leg_address,
                chanqun=chanqun,
                fcz_id=fcz_id,
                fcz_number=fcz_number,
                fcz_picture=fcz_picture,
                zufang_picture=zufang_picture,
                year=datetime.datetime.now().strftime('%Y'),
                status=0,
                utype=0,
                # 以下为空字符串，此页面不需要
                hukou_id=0,
                hukou_m='',
                hukou_s='',
                hukou_f='',
                real_address='',
                danqin='',
                one_child='',
                huji_other='',
                hukou_picture='',

            )
            self.db.add(baseinfo)
            self.db.commit()
            if baseinfo.id:
                self.write({
                    'code': 'ok',
                    'result': baseinfo.id
                })
            else:
                self.write({'code': 'error', 'result': '添加失败'})


class EnrollSecondHandler(BaseHandler):
    """
    小学预报名第二页保存
    /primaryStudent/enroll/second
    """
    @login_required([0])
    def post(self):
        id = self.get_argument("id")
        baseinfo = self.db.query(PrimaryStudents).get(id)
        if not baseinfo or baseinfo.status != 0:
            self.write({'code': 'error'})
            return
        baseinfo.hukou_s = self.get_argument("hukou_s", '')
        baseinfo.hukou_id = self.get_argument("hukou_id", '')
        baseinfo.hukou_f = self.get_argument("hukou_f", '')
        baseinfo.hukou_m = self.get_argument("hukou_m", '')
        baseinfo.danqin = self.get_argument("danqin", '')
        baseinfo.real_address = self.get_argument("real_address", '')
        baseinfo.one_child = self.get_argument("one_child", '')
        baseinfo.hukou_id = self.get_argument("hukou_id", '')
        baseinfo.huji_other = self.get_argument("huji_other", '')
        baseinfo.hukou_picture = self.get_argument("hukou_picture", '')
        self.db.commit()
        self.write({
            'code': 'ok',
            'result': baseinfo.id
        })


class EnrollSubmitHandler(BaseHandler):
    """
    小学预报名提交
    /primaryStudent/enroll/submit
    """
    @login_required([0])
    def post(self):
        id = self.get_argument("id", '')
        primary_students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.status == 0,
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.id == id
        ).first()
        if not primary_students:
            self.write({'code': 'error'})
            return
        # 只能由填报人提交
        if primary_students.uid != self.user_id:
            self.write({'code': 1402})
            return
        # status设置为1，则已提交
        primary_students.status = 1
        self.db.commit()
        self.write({
            'code': 'ok',
            'result': primary_students.id
        })