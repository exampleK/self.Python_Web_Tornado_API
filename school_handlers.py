"""
小学招生-学校接口
"""
from sitebase.base import BaseHandler, login_required
from sitebase.models import PrimaryStudents, CheckRecord, Family
from sitebase.utils import sa_rs2ds, datetime_str
# import datetime
import json


class StudentUpdateHandler(BaseHandler):
    """
    /primarySchool/student/update
    学校-学生信息-编辑或新增
    """
    @login_required([1])
    def post(self):
        args = {}
        for k, v in self.request.body_arguments.items():
            v = v[0].decode().strip()
            args[k] = v
        id_card = args['id_card']
        exist = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id_card == id_card,
            PrimaryStudents.year == self.this_year
        ).first()
        if exist:
            self.write({'code': 'error', 'msg': '该身份证已报名'})
            return
        id = int(args['id'])
        del args['id']
        family = json.loads(args['family'])
        del args['family']
        if id == 0:
            args['year'] = self.this_year
            args['uid'] = self.user_id
            # 如果是学校，school_id 使用该学校的id；如果是教育局直接使用前端传的schoo_id 教育局可以选择学校
            if self.current_user['role'] == 1:
                args['school_id'] = self.current_user['org_id']
            # 新增的学生默认的状态  学校不能新增积分生
            if args['utype'] == '1':
                # 地段生
                status = 8
            elif args['utype'] == '2':
                # 统筹生
                status = 5
            elif args['utype'] == '4':
                # 择校生
                status = 8
            args['status'] = status
            user = PrimaryStudents(**args)
            self.db.add(user)
            self.db.commit()
            if user.id:
                for fam in family:
                    fam['uid'] = user.id
                    if not fam['id_card']:
                        continue
                    fams = Family(**fam)
                    self.db.add(fams)
                self.db.commit()
                self.write({'code': 'ok', 'msg': '新增学生成功！'})
        else:
            user = self.db.query(PrimaryStudents).get(id)
            if not user:
                self.write({'code': 'error', 'msg': '参数错误'})
                return
            self.db.query(PrimaryStudents).filter(
                PrimaryStudents.id == id
            ).update(**args)
            for fam in family:
                if not fam['id_card']:
                    continue
                fams = Family(**fam)
                self.db.add(fams)
            self.db.commit()
            self.write({'code': 'ok', 'msg': '编辑成功'})


class StudentsHandler(BaseHandler):
    """
    学校小学学生管理
    /primary/school/students
    """
    @login_required([1])
    def get(self):
        school_id = self.current_user.get('org_id', '')
        utype = self.get_argument("utype", 'all')
        status = self.get_argument("status", 'all')
        page_size = int(self.get_argument("page_size", 20))
        page = int(self.get_argument("page", 1))
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status >= 5
        )
        if utype != 'all':
            students = students.filter(
                PrimaryStudents.utype == utype
            )
        if status != 'all':
            students = students.filter(
                PrimaryStudents.status == status
            )
        total = students.count()
        students = students.limit(page_size).offset(
            page_size * (page - 1)).all()
        self.write({
            'code': 'ok',
            'result': sa_rs2ds(students),
            'total': total,
            'page': page,
            'page_size': page_size
        })


class StudentsSearchHandler(BaseHandler):
    """
    学校  小学学生管理搜索
    /primarySchool/students/search
    """
    @login_required([1])
    def post(self):
        school_id = self.current_user.get('org_id', '')
        id_card = self.get_argument("id_card", '')
        fullname = self.get_argument("fullname", '')
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status >= 5
        )
        if id_card:
            students = students.filter(
                PrimaryStudents.id_card == id_card
            )
        if fullname:
            students = students.filter(
                PrimaryStudents.fullname == fullname
            )
        self.write({
            'code': 'ok',
            'result': sa_rs2ds(students)
        })


class SchoolPreviousHandler(BaseHandler):
    """
    学校历届列表
    /primarySchool/previous/list
    """
    @login_required([1])
    def get(self):
        school_id = self.current_user['org_id']
        year = self.get_argument("year", '')
        status = self.get_argument("status", 'all')
        utype = self.get_argument("utype", '')

        pagesize = int(self.get_argument("pagesize", '20'))
        current_page = int(self.get_argument("current_page", '1'))

        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.status.in_([10, 11, 12, 13]),
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.year == year,
            PrimaryStudents.utype == utype
        )

        if status != 'all' and status.isdigit():
            students = students.filter(PrimaryStudents.status == status)
        total = students.count()
        students = students.limit(pagesize).offset(
            pagesize * (current_page - 1)).all()

        self.write({
            'code': 'ok',
            'result': sa_rs2ds(students),
            'total': total,
            'page_size': pagesize,
            'page': current_page
        })


class SchoolPreviousSearchHandler(BaseHandler):
    """
    历届查询
    /primarySchool/previous/search
    """
    @login_required([1])
    def post(self):
        school_id = self.current_user['org_id']
        id_card = self.get_argument("id_card", '')
        fullname = self.get_argument("fullname", '')
        data = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.status.in_([10, 11, 12, 13])
        )
        if id_card:
            data = data.filter(PrimaryStudents.id_card == id_card)
        if fullname:
            data = data.filter(PrimaryStudents.fullname == fullname)
        data = data.all()
        self.write({
            'code': 'ok',
            'result': sa_rs2ds(data)
        })


class StudentsConfirmHandler(BaseHandler):
    """
    小学学校批量确认学生
    /primarySchool/students/confirm
    @raw json student.id array
    """
    @login_required([1])
    def post(self):
        student_ids = json.loads(self.request.body.decode())
        if not student_ids:
            self.write({'code': 'error', 'msg': '请求错误'})
            return
        # 学生状态必须是“待学校确认” 更新为“已录取”
        self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id.in_(student_ids),
            PrimaryStudents.status == 6
        ).update({'status': 10}, synchronize_session=False)
        self.db.commit()
        self.write({'code': 'ok'})


class StudentConfirmHandler(BaseHandler):
    """
    小学学校确认学生
    @同意
    @拒绝 原因
    /primarySchool/student/confirm
    """
    @login_required([1])
    def post(self):
        remark = self.get_argument("remark", '')
        tag = self.get_argument("tag", '')
        id = self.get_argument("id", '')
        student = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status == 6,
            PrimaryStudents.id == id
        ).first()
        if not student:
            self.write({'code': 'error', 'msg': 'arg id error'})
            return
        new_status = 0
        if tag == 'yes':
            # 确认后 已录取
            student.status = 10
            new_status = 10
        elif tag == 'no':
            student.status = 7
            new_status = 7
        else:
            self.write({'code': 'error', 'msg': 'tag error'})
            return
        if remark != '':
            '''
            创建审核记录
            '''
            checkRecord = CheckRecord(
                remark=remark,
                user_id=self.user_id,
                tag=1,
                created=datetime_str(),
                student_id=student.id,
                status=new_status
            )
            self.db.add(checkRecord)
        self.db.commit()
        self.write({'code': 'ok'})


class StudentRegisterHandler(BaseHandler):
    """
    /primarySchool/student/register
    学校修改状态已录取的小学生
    已报到或未报到
    """
    @login_required([1])
    def post(self):
        remark = self.get_argument("remark", '')
        tag = self.get_argument("tag", '')
        if tag not in ['yes', 'no']:
            self.write({'code': 'error', 'msg': 'arg tag error'})
            return
        id = self.get_argument("id", '')
        # 只查询今年的已录取的学生
        student = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status == 10,
            PrimaryStudents.id == id
        ).first()
        if not student:
            self.write({'code': 'error', 'msg': 'arg id error'})
            return
        new_status = 0
        if tag == 'yes':
            # 学校确认报到后，学生状态改为已报到。
            new_status = 11
            student.status = new_status
        if tag == 'no':
            # 学校确认未报到后，学生状态改为未报到。
            new_status = 12
            student.status = new_status
        if remark != '':
            '''
            创建审核记录
            '''
            checkRecord = CheckRecord(
                remark=remark,
                user_id=self.user_id,
                tag=1,
                created=datetime_str(),
                student_id=student.id,
                status=new_status
            )
            self.db.add(checkRecord)
        self.db.commit()
        self.write({'code': 'ok', 'msg': '操作成功'})


class SchoolCheckListHandler(BaseHandler):
    """
    学校审核列表
    /primarySchool/check/list
    """
    @login_required([1])
    def get(self):
        school_id = self.current_user['org_id']
        year = self.this_year
        pagesize = int(self.get_argument("pagesize", '20'))
        current_page = int(self.get_argument("current_page", '1'))
        status = self.get_argument("status", 'all')
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.status.in_([1, 2, 3, 4]),
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.year == year
        )
        if status != 'all':
            students = students.filter(PrimaryStudents.status == status)
        total = students.count()
        students = students.limit(pagesize).offset(
            pagesize * (current_page - 1)).all()

        self.write({
            'code': 'ok',
            'result': sa_rs2ds(students),
            'total': total,
            'page_size': pagesize,
            'page': current_page
        })


class SchoolCheckSearchHandler(BaseHandler):
    """
    审核查询
    /primarySschool/check/search
    """

    @login_required([1])
    def post(self):
        school_id = self.current_user['org_id']
        id_card = self.get_argument("id_card", '')
        fullname = self.get_argument("fullname", '')
        data = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.school_id == school_id,
            PrimaryStudents.status.in_([1, 2, 3, 4]),
            PrimaryStudents.year == self.this_year
        )
        if id_card:
            data = data.filter(PrimaryStudents.id_card == id_card)
        if fullname:
            data = data.filter(PrimaryStudents.fullname == fullname)
        data = data.all()
        self.write({
            'code': 'ok',
            'result': sa_rs2ds(data)
        })


class PrimaryVerifyHandler(BaseHandler):
    """
    预审核状态修改
    /primarySschool/check/verify
    """
    @login_required([1])
    def post(self):
        # 预审核状态
        YSH_STATUS = ['2', '3']
        id = self.get_argument("id", '')
        new_status = self.get_argument("new_status", '')
        if new_status not in YSH_STATUS:
            self.write({
                'code': 'error',
                'msg': 'wrong new_status'
            })
            return
        school_id = self.current_user['org_id']
        # 学生类型 ['0', '1', '2'] 未知,地段生,统筹生
        utype = self.get_argument("utype", '0')
        if utype not in ['0', '1', '2']:
            self.write({
                'code': 'error',
                'msg': 'wrong utype'
            })
            return
        remark = self.get_argument("remark", '')
        user_id = self.user_id

        update_status = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.status == 1,
            PrimaryStudents.id == id,
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.school_id == school_id
        ).first()

        if not update_status:
            self.write({
                'code': 'error',
                'msg': 'wrong id'
            })
            return
        update_status.status = new_status
        update_status.utype = utype
        '''
        创建审核记录
        '''
        checkRecord = CheckRecord(
            remark=remark,
            user_id=user_id,
            tag=1,
            created=datetime_str(),
            student_id=update_status.id,
            status=new_status
        )
        self.db.add(checkRecord)
        self.db.commit()
        self.write({'code': 'ok'})


class PrimarylocalVerifyHandler(BaseHandler):
    """
    现场审核状态修改
    /primarySchool/check/localverify

    """

    @login_required([1])
    def post(self):
        # 现场审核
        XCSH_STATUS = ['4', '5', '8']
        id = self.get_argument("id", '')
        new_status = self.get_argument("new_status", '')
        if new_status not in XCSH_STATUS:
            self.write({
                'code': 'error',
                'msg': 'wrong new_status'
            })
            return
        school_id = self.current_user['org_id']
        utype = self.get_argument("utype", '0')
        if utype not in ['0', '1', '2']:
            self.write({
                'code': 'error',
                'msg': 'wrong utype'
            })
            return
        remark = self.get_argument("remark", '')
        user_id = self.user_id
        update_status = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.status.in_([1, 2, 3, 4]),
            PrimaryStudents.id == id,
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.school_id == school_id
        ).first()
        if not update_status:
            self.write({
                'code': 'error',
                'msg': '请求错误'
            })
            return
        update_status.status = new_status
        if utype == '0' and new_status in [5, 8]:
            self.write({
                'code': 'error',
                'msg': '学生类型必选'
            })
            return
        update_status.utype = utype
        checkRecord = CheckRecord(
            remark=remark,
            user_id=user_id,
            tag=1,
            created=datetime_str(),
            student_id=update_status.id,
            status=new_status
        )
        self.db.add(checkRecord)
        self.db.commit()
        self.write({
            'code': 'ok',
            'msg': '操作成功'
        })
