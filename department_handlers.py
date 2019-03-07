"""
小学招生-教育局接口
"""
from sitebase.base import BaseHandler, login_required
from sitebase.models import PrimaryStudents, Family, School, CheckRecord
from sitebase.utils import sa_rs2ds, datetime_str
import json


class StudentUpdateHandler(BaseHandler):
    """
    /department/primaryStudent/update
    教育局小学学生信息编辑或新增
    """
    @login_required([3])
    def post(self):
        args = {}
        for k, v in self.request.body_arguments.items():
            v = v[0].decode().strip()
            args[k] = v
        id_card = args['id_card'].strip()
        exist = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id_card == id_card,
            PrimaryStudents.year == self.this_year
        ).first()
        if exist:
            self.write({'code': 'error', 'msg': '该身份证已存在'})
            return
        id = int(args['id'])
        del args['id']
        family = json.loads(args['family'])
        del args['family']
        if id == 0:
            args['year'] = self.this_year
            args['uid'] = self.user_id
            args['status'] = 6
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
            status = int(args['status'])
            # FIXME 状态修改判断
            if status > 7:
                self.write({'code': 'error', 'msg': '类型无法修改'})
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
    小学教育局-学生管理
    /department/primaryStudents
    """
    @login_required([3])
    def get(self):
        school_id = self.get_argument("school_id", 'all')
        utype = self.get_argument("utype", 'all')
        status = self.get_argument("status", 'all')
        page_size = int(self.get_argument("page_size", 20))
        page = int(self.get_argument("page", 1))
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status >= 1
        )
        if school_id != 'all':
            students = students.filter(
                PrimaryStudents.school_id == school_id
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
    搜索
    /department/primaryStudents/Search
    """
    @login_required([3])
    def post(self):
        id_card = self.get_argument("id_card", '')
        fullname = self.get_argument("fullname", '')
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status >= 1
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


class StudentConfirmHandler(BaseHandler):
    """
    教育局确认小学学生
    @同意
    @拒绝 原因
    /department/primaryStudent/confirm
    """
    @login_required([3])
    def post(self):
        remark = self.get_argument("remark", '')
        tag = self.get_argument("tag", '')
        id = self.get_argument("id", '')
        student = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.year == self.this_year,
            PrimaryStudents.status == 8,
            PrimaryStudents.id == id
        ).first()
        if not student:
            self.write({'code': 'error', 'msg': 'arg id error'})
            return
        new_status = 0
        if tag == 'yes':
            # 教育局确认后 已录取10
            student.status = 10
            new_status = 10
        elif tag == 'no':
            student.status = 9
            new_status = 9
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


class StudentsConfirmHandler(BaseHandler):
    """
    教育局批量确认学生
    /department/students/confirm
    @raw json student.id array
    """
    @login_required([3])
    def post(self):
        student_ids = json.loads(self.request.body.decode())
        if not student_ids:
            self.write({'code': 'error', 'msg': '请求错误'})
            return
        # 学生状态必须是“待教育局确认” 更新为“已录取”
        self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id.in_(student_ids),
            PrimaryStudents.status == 8
        ).update({'status': 10})
        self.db.commit()
        self.write({'code': 'ok'})


class StudentsAssignHandler(BaseHandler):
    """
    /department/primaryStudents/assign
    教育局批量给小学学生分配某个学校
    """
    @login_required([3])
    def post(self):
        data = json.loads(self.request.body.decode())
        school_id = data.get('school_id', 0)
        # 查询这个学校是否是正常的小学
        school = self.db.query(School).filter(
            School.type == 1,
            School.id == school_id,
            School.status == 0
        ).first()
        if not school:
            self.write({'code': 'error', 'msg': '学校错误'})
            return
        student_ids = data.get("uids", [])
        if not school_id or not student_ids:
            self.write({'code': 'error', 'msg': '请求错误'})
            return
        # 学生状态必须是待分配 更新为待学校确认
        self.db.query(PrimaryStudents).filter(
            PrimaryStudents.id.in_(student_ids),
            PrimaryStudents.status == 5
        ).update({'school_id': school_id, 'status': 6}, synchronize_session=False)
        self.db.commit()
        self.write({'code': 'ok'})


class PreviousHandler(BaseHandler):
    """
    教育局小学学校历届招生
    /department/primaryPrevious
    """
    @login_required([3])
    def get(self):
        school_id = self.get_argument("school_id", '')
        year = self.get_argument("year", '')
        status = self.get_argument("status", 'all')
        utype = self.get_argument("utype", '')
        pagesize = int(self.get_argument("pagesize", '20'))
        current_page = int(self.get_argument("current_page", '1'))
        students = self.db.query(PrimaryStudents).filter(
            PrimaryStudents.school_id == school_id,
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


class PreviousSearchHandler(BaseHandler):
    """
    教育局小学学校历届招生
    /department/primaryPrevious/search
    """
    @login_required([3])
    def post(self):
        id_card = self.get_argument("id_card", '').strip()
        fullname = self.get_argument("fullname", '')
        data = self.db.query(PrimaryStudents).filter(
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
