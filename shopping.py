import pymysql
import time
'''这个程序实现数据库交互'''


class ShangHui(object):
    # _instance = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super(ShangHui, cls).__new__(cls, *args, **kwargs)
    #         return cls._instance

    def __init__(self):
        '''
        初始化数据库'''
        self.connect_obj = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            database='commodity',
            user='root',
            password='mysql',
            charset='utf8')
        self.cur = self.connect_obj.cursor()  # 操作
        self.login_name = ''  # 登录之后的用户名
        self.login_flag = 0  # 登陆验证

    def close(self):
        self.connect_obj.close()
        self.cur.close()
        print('再见')

    def login(self, user_info):
        '''这个是登录操作,返回一个布尔值'''
        #  username=zzz&password=123 取出名字和密码
        try:
            split_info = user_info.split('&')
            inname = split_info[0][9:]
            inpassword = split_info[1][9:]
        except :
            print('数据没有传输过来')
            return False

        # 不要用拼接sql字符串
        sql = 'SELECT * FROM user WHERE name=%s and password=%s'
        try:
            # 参数列表化
            ret = self.cur.execute(sql, [inname, inpassword])
        except Exception as e:
            ret = '数据库出错'
            print(e)
        if ret == 0:
            print('账号或密码出错')
            return False
        print('#########登录成功###########')
        self.login_name = inname
        self.login_flag = 1
        return True

    def get_data_str(self):
        print('商品展示')
        try:
            sql = '''SELECT commodity.name AS'商品名',commodity.price AS'价格',cate.name AS'商品类别',brand.name AS'商品品牌' FROM commodity INNER JOIN cate ON commodity.cate_id=cate.id INNER JOIN brand ON commodity.brand_id=brand.id'''
            ret = self.cur.execute(sql)
            if ret:
                data_str = '商品名  价格  商品类别  品牌<br>'
                for i in self.cur.fetchall():
                    for j in i:
                        str1 = str(j)
                        data_str += str1 + '  '
                    data_str += '<br>'
                print(data_str)
                return data_str
        except Exception as e:
            print(e)

    def get_order_id(self):
        # 这是读写文件，目的是为了保存并读取订单id,每次自增1
        file_data = ''
        with open('order.txt', 'r') as f:

            for line in f:
                old_str = line
                new_str = str(int(old_str) + 1)
                file_data = new_str
        with open('order.txt', 'w') as f:
            f.write(file_data)
        # 最后异步读取
        with open('order.txt', 'r') as f:

            for line in f:
                file_data = line
        return file_data

    def order_comm(self, order_info):
        '''下订单，判断可不可以'''
        #  name=zzz&num=1 取出名字和密码
        try:
            split_info = order_info.split('&')
            order_name = split_info[0][5:]  # 这里编码问题
        except:
            print('数据没有传输')
            return False

        print('商品下单', order_name)
        try:
            sql = 'SELECT price FROM commodity WHERE name=%s'
            ret = self.cur.execute(sql, [order_name, ])
            if ret:
                print('下单成功，下面输入配送信息')
                return True
            else:
                print('输入错误,返回主界面')
                return False
        except Exception as e:
            print(e)

    def confirm_order(self, add_info, order_info, sys_name):
        # 订单确认，然后写入订单表，订单详情表，配送表，
        #  name=zzz&phone=11132112&address=sdasda 取出名字和密码
        try:
            # 切割用户信息
            split_info = add_info.split('&')
            user_name = split_info[0][5:]
            user_phone = split_info[1][6:]
            user_addr = split_info[2][8:]
        except:
            print('数据没有传输')
            return
        # 切割订单
        split_order = order_info.split('&')
        print('############')
        print(split_order)
        order_name = split_order[0][5:]  # 商品名字
        order_num = int(split_order[1][4:])
        # 挑选并确认价格
        sql = 'SELECT price FROM commodity WHERE name=%s'
        self.cur.execute(sql, [order_name, ])
        pay_price = self.cur.fetchall()[0][0]
        payment = order_num * pay_price  # 总价

        # 获得用户id
        try:
            user_sql = 'SELECT id FROM user WHERE name=%s'
            self.cur.execute(user_sql, [sys_name, ])
            user_id = self.cur.fetchone()[0]
            # 获得商品id
            comm_sql = 'SELECT id FROM commodity WHERE name=%s'
            self.cur.execute(comm_sql, [order_name])
            comm_id = self.cur.fetchone()[0]
            print('写入订单表')
            # 写入订单表 id,payment,pay_time,user_id,send_time
            order_sql = 'INSERT INTO myorder VALUES(0, %s, %s, %s, %s)'
            self.cur.execute(order_sql, [payment, time.ctime(), user_id, '一天后'])

            # 获得订单id 用文件存储方法
            order_id = int(self.get_order_id())
            print('写入订单详情表')
            # 写入订单详情表 id,comm_id,order_id,num,price,total_fee
            items_sql = 'INSERT INTO order_items VALUES(0, %s, %s, %s, %s, %s)'
            self.cur.execute(items_sql, [comm_id, order_id, order_num, pay_price, payment])
            # 写入配送表 id,order_id,user_id,name,phone,address
            print('写入配送表')
            ship_sql = 'INSERT INTO shipping VALUES(0, %s, %s, %s, %s, %s)'
            self.cur.execute(ship_sql, [order_id, user_id, user_name, user_phone, user_addr])

            self.connect_obj.commit()  # 写入

        except Exception as e:
            print(e)

    def signin(self, user_info):
        '''注册注意数据库保存'''
        #  reg_username=zzz&password=123 取出名字和密码
        split_info = user_info.split('&')
        inname = split_info[0][13:]
        inpassword = split_info[1][9:]
        print('注册账号')
        try:
            sql = 'SELECT * FROM user WHERE name=%s'
            ret = self.cur.execute(sql, [inname, ])
            if ret:
                print('用户名已经存在')
                return False
            sql_insert = 'INSERT INTO user VALUES(0, %s, %s)'
            ret1 = self.cur.execute(sql_insert, [inname, inpassword])
            if ret1:
                print('注册成功')
                self.connect_obj.commit()  # 提交
                return True

        except Exception as e:
            print(e)

    def change_password(self, user_info):
        '''注册注意数据库保存'''
        #  username=zzz&old_psd=123&new_psd=333 取出名字和密码
        split_info = user_info.split('&')
        user_name = split_info[0][9:]
        old_password = split_info[1][8:]
        print('修改密码')
        new_password = split_info[2][8:]
        try:
            sql = 'SELECT * FROM user WHERE name=%s and password=%s'
            ret = self.cur.execute(sql, [user_name, old_password])
            if ret == 0:
                print('旧密码输入错误')
                return False
            else:
                sql_update = 'UPDATE user SET password=%s WHERE name=%s'
                ret1 = self.cur.execute(sql_update, [new_password, user_name])
                if ret1:
                    print('修改成功')
                self.connect_obj.commit()  # 提交
                return True
        except Exception as e:
            print(e)

    def get_check_order(self):
        print('订单展示')
        try:
            sql = '''SELECT myorder.id,myorder.,cate.name AS'商品类别',brand.name AS'商品品牌' FROM commodity INNER JOIN cate ON commodity.cate_id=cate.id INNER JOIN brand ON commodity.brand_id=brand.id'''
            ret = self.cur.execute(sql)
            if ret:
                data_str = '商品名  价格  商品类别  品牌<br>'
                for i in self.cur.fetchall():
                    for j in i:
                        str1 = str(j)
                        data_str += str1 + '  '
                    data_str += '<br>'
                print(data_str)
                return data_str
        except Exception as e:
            print(e)

