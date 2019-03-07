from sitebase.base import BaseHandler
from sitebase.base import BaseHandler, login_required
from sitebase.models import PrimaryStudents, CheckRecord, Family
import os
import datetime
import re
import xlrd


class PrimaryZxsHandler(BaseHandler):
    """
    /import/primary/zxs
    导入小学择校生
    """
    '''
    导入分为两步
    第一步 检查 for循环xlw表格 ，如果有错误则不进行第二步
    第二部 写入 for循环xlw表格
    
    待处理：第一步和第二步都各有一个相同for循环，冗余
    '''
    def post(self):
        school_id = self.current_user.get('org_id', '')
        # school_id = 14

        file_address = self.get_argument("file_address", '')
        # file_address = (r'/home/wangkai/sgx_enrollment/website/static/primarystudentupload/test11.xlsx')

        # 定义一个list记录错误日志
        import_log = {}

        # 读取文件
        data = xlrd.open_workbook(file_address)
        # 通过索引顺序获取 ：sheet 0 就是第一个
        table = data.sheets()[0]
        """     
        # 通过索引顺序获取
        table = data.sheet_by_index(0)
        # 通过名称获取 ：sheet name 就是名字
        table = data.sheet_by_name(u'category') 
        """

        # 获取整行的值（数组）
        table.row_values(1)
        # 获取整列的值（数组）
        table.col_values(1)
        # 获取行数　　
        nrows = table.nrows
        # 获取列数
        # ncols = table.ncols

        # 循环行列表数据
        for i in range(1, nrows):  # 从第一行开始至结尾，修改数字可以改变起始行
            # print(table.row_values(i)) #type:list
            # 接收的参数全是float类型，所以得转换
            e_fullname = (table.row_values(i))[2]
            e_id_card = int((table.row_values(i))[3])
            e_gender = (table.row_values(i))[4]
            e_nationality = (table.row_values(i))[5]
            e_native_place = (table.row_values(i))[6]
            e_ethnic = (table.row_values(i))[7]
            e_birthdate = (table.row_values(i))[8]
            e_is_gat = (table.row_values(i))[9]
            e_heath = (table.row_values(i))[10]
            e_yfjzz = (table.row_values(i))[11]
            e_kindergarten = (table.row_values(i))[12]
            e_birth_id = (table.row_values(i))[13]

            leg_address1 = str((table.row_values(i))[14])
            leg_address2 = str((table.row_values(i))[15])
            leg_address3 = str((table.row_values(i))[16])

            chanqun = (table.row_values(i))[17]
            fcz_id = (table.row_values(i))[18]
            fcz_number = (table.row_values(i))[19]
            hukou_id = (table.row_values(i))[20]

            real_address1 = str((table.row_values(i))[21])
            real_address2 = str((table.row_values(i))[22])
            real_address3 = str((table.row_values(i))[23])
            real_address4 = str((table.row_values(i))[24])

            hukou_f = (table.row_values(i))[25]
            hukou_m = (table.row_values(i))[26]

            real_address = (table.row_values(i))[27]
            # yes_no
            e_danqin = (table.row_values(i))[28]
            e_one_child = (table.row_values(i))[29]
            e_huji_other = (table.row_values(i))[30]

            # mother and father
            e_utype1 = (table.row_values(i))[31]
            e_fullname1 = (table.row_values(i))[32]
            e_id_card1 = int((table.row_values(i))[33])
            e_phone1 = (table.row_values(i))[34]
            e_education1 = (table.row_values(i))[35]
            birthdate1 = (table.row_values(i))[36]
            mail1 = (table.row_values(i))[37]
            fixed_phone1 = (table.row_values(i))[38]
            address1 = (table.row_values(i))[39]
            company1 = (table.row_values(i))[40]
            office1 = (table.row_values(i))[41]

            e_utype2 = (table.row_values(i))[42]
            e_fullname2 = (table.row_values(i))[43]
            e_id_card2 = int((table.row_values(i))[44])
            e_phone2 = (table.row_values(i))[45]
            e_education2 = (table.row_values(i))[46]
            birthdate2 = (table.row_values(i))[47]
            mail2 = (table.row_values(i))[48]
            fixed_phone2 = (table.row_values(i))[49]
            address2 = (table.row_values(i))[50]
            company2 = (table.row_values(i))[51]
            office2 = (table.row_values(i))[52]

            '''
            导入判断
            ---身份证
            '''
            exist = self.db.query(PrimaryStudents).filter(
                PrimaryStudents.id_card == e_id_card,
                PrimaryStudents.year == datetime.datetime.now().strftime('%Y')
            ).first()
            if exist:
                import_log[e_id_card] = '该身份证已报名'
                # 身份如果已填报，就不继续检查该学生其他信息
            else:
                '''
                导入判断
                ---必填为空,如果身份证没有填报，接着检查
                '''
                xx =0
                def x():
                    nonlocal xx
                    xx+=1
                    return xx
                if len(str(e_fullname)) == 0 and len(e_id_card) == 0 \
                        and len(e_gender) == 0 and len(e_nationality) == 0 \
                        and len(e_native_place) == 0 and len(e_ethnic) == 0 \
                        and len(e_birthdate) == 0 and len(e_is_gat) == 0 \
                        and len(e_heath) == 0 and len(e_yfjzz) == 0 \
                        and len(e_kindergarten) == 0 and len(e_birth_id) == 0:
                    pass

                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag0]该用户有未填写内容'
                '''
                判断是否三项
                '''
                if len(e_danqin) == 0 and len(e_one_child) == 0 and len(e_huji_other):
                    pass
                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag101]在是否选项中为空'

                yesnot_list = ['是', '否']
                if e_danqin in yesnot_list and e_one_child in yesnot_list and e_huji_other in yesnot_list:
                    pass
                else:
                    import_log['-该用户id：'+str(e_id_card)+'-第'+str(x())+'个错误'] = '[flag102]在是否选项中只能是或者否'
                '''
                检查父母
                '''
                if e_danqin == '否':
                    if len(e_utype1) == 0 and len(e_fullname1) == 0 and len(e_id_card1) == 0 and len(e_phone1) == 0 and len(e_education1) == 0 and len(e_utype2) == 0 and len(e_fullname2) == 0 and len(e_id_card2) == 0 and len(e_phone2) == 0 and len(e_education2) == 0:
                        import_log['-该用户id：' + e_id_card + '的第' + str(x()) + '个错误'] = '[flag201]该用户家长有未填写内容'

                elif e_danqin == '是':
                    '''
                    检查父或者母
                    '''
                    if (len(e_utype1) == 0 and len(e_fullname1) == 0 and len(e_id_card1) == 0 and len(
                            e_phone1) == 0 and len(e_education1) == 0) or \
                            (len(e_utype2) == 0 and len(e_fullname2) == 0 and len(e_id_card2) == 0 and len(
                                e_phone2) == 0 and len(e_education2) == 0):
                        import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag202]该用户家长有未填写内容'
                    else:
                        pass
                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag203]是否单亲只能输入是或者否'
        '''
        如果没有错误，则执行
        '''
        if import_log:

            self.write(import_log)
            return
        else:
            for i in range(1, nrows):  # 从第一行开始至结尾，修改数字可以改变起始行
                # print(table.row_values(i)) #type:list
                # 接收的参数全是float类型，所以得转换
                e_fullname = (table.row_values(i))[2]
                e_id_card = int((table.row_values(i))[3])
                e_gender = (table.row_values(i))[4]
                e_nationality = (table.row_values(i))[5]
                e_native_place = (table.row_values(i))[6]
                e_ethnic = (table.row_values(i))[7]
                e_birthdate = (table.row_values(i))[8]
                e_is_gat = (table.row_values(i))[9]
                e_heath = (table.row_values(i))[10]
                e_yfjzz = (table.row_values(i))[11]
                e_kindergarten = (table.row_values(i))[12]
                e_birth_id = (table.row_values(i))[13]

                leg_address1 = str((table.row_values(i))[14])
                leg_address2 = str((table.row_values(i))[15])
                leg_address3 = str((table.row_values(i))[16])

                chanqun = (table.row_values(i))[17]
                fcz_id = (table.row_values(i))[18]
                fcz_number = (table.row_values(i))[19]
                hukou_id = (table.row_values(i))[20]

                real_address1 = str((table.row_values(i))[21])
                real_address2 = str((table.row_values(i))[22])
                real_address3 = str((table.row_values(i))[23])
                real_address4 = str((table.row_values(i))[24])

                hukou_f = (table.row_values(i))[25]
                hukou_m = (table.row_values(i))[26]

                real_address = (table.row_values(i))[27]
                # yes_no
                e_danqin = (table.row_values(i))[28]
                e_one_child = (table.row_values(i))[29]
                e_huji_other = (table.row_values(i))[30]

                # mother and father
                e_utype1 = (table.row_values(i))[31]
                e_fullname1 = (table.row_values(i))[32]
                e_id_card1 = int((table.row_values(i))[33])
                e_phone1 = (table.row_values(i))[34]
                e_education1 = (table.row_values(i))[35]
                birthdate1 = (table.row_values(i))[36]
                mail1 = (table.row_values(i))[37]
                fixed_phone1 = (table.row_values(i))[38]
                address1 = (table.row_values(i))[39]
                company1 = (table.row_values(i))[40]
                office1 = (table.row_values(i))[41]

                e_utype2 = (table.row_values(i))[42]
                e_fullname2 = (table.row_values(i))[43]
                e_id_card2 = int((table.row_values(i))[44])
                e_phone2 = (table.row_values(i))[45]
                e_education2 = (table.row_values(i))[46]
                birthdate2 = (table.row_values(i))[47]
                mail2 = (table.row_values(i))[48]
                fixed_phone2 = (table.row_values(i))[49]
                address2 = (table.row_values(i))[50]
                company2 = (table.row_values(i))[51]
                office2 = (table.row_values(i))[52]
                '''
                创建表
                '''
                add_s_info = PrimaryStudents(
                    school_id=school_id,
                    uid='',
                    fullname=e_fullname,
                    id_card=e_id_card,
                    gender=e_gender,
                    nationality=e_nationality,
                    native_place=e_native_place,
                    ethnic=e_ethnic,
                    birthdate=e_birthdate,
                    is_gat=e_is_gat,
                    heath=e_heath,
                    yfjzz=e_yfjzz,
                    kindergarten=e_kindergarten,
                    birth_id=e_birth_id,
                    avatar='',
                    leg_address=leg_address1 + '-' + leg_address2 + '-' + leg_address3,
                    chanqun=chanqun,
                    fcz_id=fcz_id,
                    fcz_number=fcz_number,
                    hukou_id=hukou_id,
                    hukou_s=real_address1 + '-' + real_address2 + '-' + real_address3 + '-' + real_address4,
                    real_address=real_address,
                    hukou_f=hukou_f,
                    hukou_m=hukou_m,
                    danqin=e_danqin,
                    one_child=e_one_child,
                    huji_other=e_huji_other,
                    fcz_picture='',
                    zufang_picture='',
                    year=datetime.datetime.now().strftime('%Y'),
                    status=8,  # 择校状态
                    utype=4,# 择校生
                    hukou_picture='',

                )
                self.db.add(add_s_info)
                self.db.commit()
                '''
                查询上一步添加的学生id，为下一步添加家长做依据
                '''
                new_data = self.db.query(PrimaryStudents).filter(
                    PrimaryStudents.id_card == e_id_card,
                    PrimaryStudents.year == datetime.datetime.now().strftime('%Y')
                ).first()
                if new_data:
                    '''
                    创建家长表
                    ---如果父母双方有一方是空字符，则那一方不创建表（之前的if已判断双亲问题这里只需要这样判断，防止单亲，给没填的一方建空表）
                    '''
                    if len(e_fullname1) == 0 and len(e_id_card1) == 0:
                        pass
                    else:
                        add_f1_info = Family(
                            uid=new_data.id,
                            tag=0,
                            utype=e_utype1,
                            fullname=e_fullname1,
                            id_card=e_id_card1,
                            birthdate=birthdate1,
                            education=e_education1,
                            phone=e_phone1,
                            office=office1,
                            company=company1,
                            address=address1,
                            mail=mail1,
                            fixed_phone=fixed_phone1
                        )
                        self.db.add(add_f1_info)
                        self.db.commit()
                    if len(e_fullname2) == 0 and len(e_id_card2) == 0:
                        pass
                    else:
                        add_f2_info = Family(
                            uid=new_data.id,
                            tag=0,
                            utype=e_utype2,
                            fullname=e_fullname2,
                            id_card=e_id_card2,
                            birthdate=birthdate2,
                            education=e_education2,
                            phone=e_phone2,
                            office=office2,
                            company=company2,
                            address=address2,
                            mail=mail2,
                            fixed_phone=fixed_phone2
                        )
                        self.db.add(add_f2_info)
                        self.db.commit()
            self.write({
                'code': 'ok'
            })

class PrimaryJfsHandler(BaseHandler):
    """
    /import/primary/zxs
    导入小学积分生
    """

    def post(self):
        # school_id = self.current_user.get('org_id', '')
        school_id = ''

        file_address = self.get_argument("file_address", '')
        # file_address = (r'/home/wangkai/sgx_enrollment/website/static/primarystudentupload/test11.xlsx')

        # 定义一个list记录错误日志
        import_log = {}

        # 读取文件
        data = xlrd.open_workbook(file_address)
        # 通过索引顺序获取 ：sheet 0 就是第一个
        table = data.sheets()[0]
        """     
        # 通过索引顺序获取
        table = data.sheet_by_index(0)
        # 通过名称获取 ：sheet name 就是名字
        table = data.sheet_by_name(u'category') 
        """

        # 获取整行的值（数组）
        table.row_values(1)
        # 获取整列的值（数组）
        table.col_values(1)
        # 获取行数　　
        nrows = table.nrows
        # 获取列数
        # ncols = table.ncols

        # 循环行列表数据
        for i in range(1, nrows):  # 从第一行开始至结尾，修改数字可以改变起始行
            # print(table.row_values(i)) #type:list
            # 接收的参数全是float类型，所以得转换
            e_fullname = (table.row_values(i))[2]
            e_id_card = int((table.row_values(i))[3])
            e_gender = (table.row_values(i))[4]
            e_nationality = (table.row_values(i))[5]
            e_native_place = (table.row_values(i))[6]
            e_ethnic = (table.row_values(i))[7]
            e_birthdate = (table.row_values(i))[8]
            e_is_gat = (table.row_values(i))[9]
            e_heath = (table.row_values(i))[10]
            e_yfjzz = (table.row_values(i))[11]
            e_kindergarten = (table.row_values(i))[12]
            e_birth_id = (table.row_values(i))[13]

            leg_address1 = str((table.row_values(i))[14])
            leg_address2 = str((table.row_values(i))[15])
            leg_address3 = str((table.row_values(i))[16])

            chanqun = (table.row_values(i))[17]
            fcz_id = (table.row_values(i))[18]
            fcz_number = (table.row_values(i))[19]
            hukou_id = (table.row_values(i))[20]

            real_address1 = str((table.row_values(i))[21])
            real_address2 = str((table.row_values(i))[22])
            real_address3 = str((table.row_values(i))[23])
            real_address4 = str((table.row_values(i))[24])

            hukou_f = (table.row_values(i))[25]
            hukou_m = (table.row_values(i))[26]

            real_address = (table.row_values(i))[27]
            # yes_no
            e_danqin = (table.row_values(i))[28]
            e_one_child = (table.row_values(i))[29]
            e_huji_other = (table.row_values(i))[30]

            # mother and father
            e_utype1 = (table.row_values(i))[31]
            e_fullname1 = (table.row_values(i))[32]
            e_id_card1 = int((table.row_values(i))[33])
            e_phone1 = (table.row_values(i))[34]
            e_education1 = (table.row_values(i))[35]
            birthdate1 = (table.row_values(i))[36]
            mail1 = (table.row_values(i))[37]
            fixed_phone1 = (table.row_values(i))[38]
            address1 = (table.row_values(i))[39]
            company1 = (table.row_values(i))[40]
            office1 = (table.row_values(i))[41]

            e_utype2 = (table.row_values(i))[42]
            e_fullname2 = (table.row_values(i))[43]
            e_id_card2 = int((table.row_values(i))[44])
            e_phone2 = (table.row_values(i))[45]
            e_education2 = (table.row_values(i))[46]
            birthdate2 = (table.row_values(i))[47]
            mail2 = (table.row_values(i))[48]
            fixed_phone2 = (table.row_values(i))[49]
            address2 = (table.row_values(i))[50]
            company2 = (table.row_values(i))[51]
            office2 = (table.row_values(i))[52]

            '''
            导入判断
            ---身份证
            '''
            exist = self.db.query(PrimaryStudents).filter(
                PrimaryStudents.id_card == e_id_card,
                PrimaryStudents.year == datetime.datetime.now().strftime('%Y')
            ).first()
            if exist:
                import_log[e_id_card] = '该身份证已报名'
                # 身份如果已填报，就不继续检查该学生其他信息
            else:
                '''
                导入判断
                ---必填为空,如果身份证没有填报，接着检查
                '''
                xx =0
                def x():
                    nonlocal xx
                    xx+=1
                    return xx
                if len(str(e_fullname)) == 0 and len(e_id_card) == 0 \
                        and len(e_gender) == 0 and len(e_nationality) == 0 \
                        and len(e_native_place) == 0 and len(e_ethnic) == 0 \
                        and len(e_birthdate) == 0 and len(e_is_gat) == 0 \
                        and len(e_heath) == 0 and len(e_yfjzz) == 0 \
                        and len(e_kindergarten) == 0 and len(e_birth_id) == 0:
                    pass

                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag0]该用户有未填写内容'
                '''
                判断是否三项
                '''
                if len(e_danqin) == 0 and len(e_one_child) == 0 and len(e_huji_other):
                    pass
                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag101]在是否选项中为空'

                yesnot_list = ['是', '否']
                if e_danqin in yesnot_list and e_one_child in yesnot_list and e_huji_other in yesnot_list:
                    pass
                else:
                    import_log['-该用户id：'+str(e_id_card)+'-第'+str(x())+'个错误'] = '[flag102]在是否选项中只能是或者否'
                '''
                检查父母
                '''
                if e_danqin == '否':
                    if len(e_utype1) == 0 and len(e_fullname1) == 0 and len(e_id_card1) == 0 and len(e_phone1) == 0 and len(e_education1) == 0 and len(e_utype2) == 0 and len(e_fullname2) == 0 and len(e_id_card2) == 0 and len(e_phone2) == 0 and len(e_education2) == 0:
                        import_log['-该用户id：' + e_id_card + '的第' + str(x()) + '个错误'] = '[flag201]该用户家长有未填写内容'

                elif e_danqin == '是':
                    '''
                    检查父或者母
                    '''
                    if (len(e_utype1) == 0 and len(e_fullname1) == 0 and len(e_id_card1) == 0 and len(
                            e_phone1) == 0 and len(e_education1) == 0) or \
                            (len(e_utype2) == 0 and len(e_fullname2) == 0 and len(e_id_card2) == 0 and len(
                                e_phone2) == 0 and len(e_education2) == 0):
                        import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag202]该用户家长有未填写内容'
                    else:
                        pass
                else:
                    import_log['-该用户id：' + str(e_id_card) + '的第' + str(x()) + '个错误'] = '[flag203]是否单亲只能输入是或者否'
        '''
        如果没有错误，则执行
        '''
        if import_log:

            self.write(import_log)
            return
        else:
            for i in range(1, nrows):  # 从第一行开始至结尾，修改数字可以改变起始行
                # print(table.row_values(i)) #type:list
                # 接收的参数全是float类型，所以得转换
                e_fullname = (table.row_values(i))[2]
                e_id_card = int((table.row_values(i))[3])
                e_gender = (table.row_values(i))[4]
                e_nationality = (table.row_values(i))[5]
                e_native_place = (table.row_values(i))[6]
                e_ethnic = (table.row_values(i))[7]
                e_birthdate = (table.row_values(i))[8]
                e_is_gat = (table.row_values(i))[9]
                e_heath = (table.row_values(i))[10]
                e_yfjzz = (table.row_values(i))[11]
                e_kindergarten = (table.row_values(i))[12]
                e_birth_id = (table.row_values(i))[13]

                leg_address1 = str((table.row_values(i))[14])
                leg_address2 = str((table.row_values(i))[15])
                leg_address3 = str((table.row_values(i))[16])

                chanqun = (table.row_values(i))[17]
                fcz_id = (table.row_values(i))[18]
                fcz_number = (table.row_values(i))[19]
                hukou_id = (table.row_values(i))[20]

                real_address1 = str((table.row_values(i))[21])
                real_address2 = str((table.row_values(i))[22])
                real_address3 = str((table.row_values(i))[23])
                real_address4 = str((table.row_values(i))[24])

                hukou_f = (table.row_values(i))[25]
                hukou_m = (table.row_values(i))[26]

                real_address = (table.row_values(i))[27]
                # yes_no
                e_danqin = (table.row_values(i))[28]
                e_one_child = (table.row_values(i))[29]
                e_huji_other = (table.row_values(i))[30]

                # mother and father
                e_utype1 = (table.row_values(i))[31]
                e_fullname1 = (table.row_values(i))[32]
                e_id_card1 = int((table.row_values(i))[33])
                e_phone1 = (table.row_values(i))[34]
                e_education1 = (table.row_values(i))[35]
                birthdate1 = (table.row_values(i))[36]
                mail1 = (table.row_values(i))[37]
                fixed_phone1 = (table.row_values(i))[38]
                address1 = (table.row_values(i))[39]
                company1 = (table.row_values(i))[40]
                office1 = (table.row_values(i))[41]

                e_utype2 = (table.row_values(i))[42]
                e_fullname2 = (table.row_values(i))[43]
                e_id_card2 = int((table.row_values(i))[44])
                e_phone2 = (table.row_values(i))[45]
                e_education2 = (table.row_values(i))[46]
                birthdate2 = (table.row_values(i))[47]
                mail2 = (table.row_values(i))[48]
                fixed_phone2 = (table.row_values(i))[49]
                address2 = (table.row_values(i))[50]
                company2 = (table.row_values(i))[51]
                office2 = (table.row_values(i))[52]
                '''
                创建表
                '''
                add_s_info = PrimaryStudents(
                    school_id=school_id,
                    uid='',
                    fullname=e_fullname,
                    id_card=e_id_card,
                    gender=e_gender,
                    nationality=e_nationality,
                    native_place=e_native_place,
                    ethnic=e_ethnic,
                    birthdate=e_birthdate,
                    is_gat=e_is_gat,
                    heath=e_heath,
                    yfjzz=e_yfjzz,
                    kindergarten=e_kindergarten,
                    birth_id=e_birth_id,
                    avatar='',
                    leg_address=leg_address1 + '-' + leg_address2 + '-' + leg_address3,
                    chanqun=chanqun,
                    fcz_id=fcz_id,
                    fcz_number=fcz_number,
                    hukou_id=hukou_id,
                    hukou_s=real_address1 + '-' + real_address2 + '-' + real_address3 + '-' + real_address4,
                    real_address=real_address,
                    hukou_f=hukou_f,
                    hukou_m=hukou_m,
                    danqin=e_danqin,
                    one_child=e_one_child,
                    huji_other=e_huji_other,
                    fcz_picture='',
                    zufang_picture='',
                    year=datetime.datetime.now().strftime('%Y'),
                    status=5,  # 择校状态
                    utype=3,# 择校生
                    hukou_picture='',

                )
                self.db.add(add_s_info)
                self.db.commit()
                '''
                查询上一步添加的学生id，为下一步添加家长做依据
                '''
                new_data = self.db.query(PrimaryStudents).filter(
                    PrimaryStudents.id_card == e_id_card,
                    PrimaryStudents.year == datetime.datetime.now().strftime('%Y')
                ).first()
                if new_data:
                    '''
                    创建家长表
                    ---如果父母双方有一方是空字符，则那一方不创建表（之前的if已判断双亲问题这里只需要这样判断，防止单亲，给没填的一方建空表）
                    '''
                    if len(e_fullname1) == 0 and len(e_id_card1) == 0:
                        pass
                    else:
                        add_f1_info = Family(
                            uid=new_data.id,
                            tag=0,
                            utype=e_utype1,
                            fullname=e_fullname1,
                            id_card=e_id_card1,
                            birthdate=birthdate1,
                            education=e_education1,
                            phone=e_phone1,
                            office=office1,
                            company=company1,
                            address=address1,
                            mail=mail1,
                            fixed_phone=fixed_phone1
                        )
                        self.db.add(add_f1_info)
                        self.db.commit()
                    if len(e_fullname2) == 0 and len(e_id_card2) == 0:
                        pass
                    else:
                        add_f2_info = Family(
                            uid=new_data.id,
                            tag=0,
                            utype=e_utype2,
                            fullname=e_fullname2,
                            id_card=e_id_card2,
                            birthdate=birthdate2,
                            education=e_education2,
                            phone=e_phone2,
                            office=office2,
                            company=company2,
                            address=address2,
                            mail=mail2,
                            fixed_phone=fixed_phone2
                        )
                        self.db.add(add_f2_info)
                        self.db.commit()
            self.write({
                'code': 'ok'
            })
