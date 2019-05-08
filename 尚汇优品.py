import pymysql
import time
'''这个程序执行模拟商城购物'''


class ShangHui(object):
    def __init__(self):
        '''初始化数据库'''
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

    def printinfo(self):
        # 写个无限循环
        while True:
            print('''欢迎来到尚汇优品商城：
                    1-登录
                    2-注册
                    3-商品展示
                    4-下单
                    5-退出''')
            choose = input('请输入需要执行的操作:\n')
            if choose == '1':
                self.login()
            elif choose == '2':
                self.signin()
            elif choose == '3':
                self.show()
            elif choose == '4':
                self.order()
            elif choose == '5':
                self.connect_obj.close()
                self.cur.close()
                print('再见')
                break
            else:
                print('输入错误，请重新输入')

    def login(self):
        print('这个是登录操作')
        inname = input('请输入用户名：')
        inpassword = input('请输入密码:')
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
            return
        print('#########登录成功###########')
        self.login_name = inname
        self.login_flag = 1

        while True:
            print('''欢迎来到尚汇优品商城：
                    1-修改密码
                    2-商品展示
                    3-下单
                    4-退出''')
            choose = input('请输入需要执行的操作:\n')
            if choose == '1':
                self.change_password()
            elif choose == '2':
                self.show()
            elif choose == '3':
                self.order()
            elif choose == '4':
                self.connect_obj.close()
                self.cur.close()
                print('再见')
                quit()
            else:
                print('输入错误，请重新输入')

    def show(self):
        print('商品展示')
        try:
            sql = '''SELECT commodity.name AS'商品名',commodity.price AS'价格',cate.name AS'商品类别',brand.name AS'商品品牌' FROM commodity INNER JOIN cate ON commodity.cate_id=cate.id INNER JOIN brand ON commodity.brand_id=brand.id'''
            ret = self.cur.execute(sql)
            if ret:
                data_str = ''
                print('商品名  价格  商品类别  品牌')
                for i in self.cur.fetchall():
                    for j in i:
                        str1 = str(j)
                        data_str += str1 + '  '
                    data_str += '\n'
                print(data_str)
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

    def order(self):
        '''订单表，订单详情表，配送表'''
        if self.login_flag:
            # 要先登录
            print('商品下单')
            order_name = input('请输入要下单商品名：')
            order_num = int(input('请输入下单数量：'))
            try:
                sql = 'SELECT price FROM commodity WHERE name=%s'
                ret = self.cur.execute(sql, [order_name, ])
                if ret:
                    print('下单成功，下面输入配送信息')
                    user_name = input('请输入您的名字：')
                    user_phone = input('请输入您的手机号码:')
                    user_addr = input('请输入您的地址:')
                    pay_price = self.cur.fetchall()[0][0]
                    payment = order_num * pay_price  # 总价

                    # 获得用户id
                    user_sql = 'SELECT id FROM user WHERE name=%s'
                    self.cur.execute(user_sql, [self.login_name])
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
                else:
                    print('输入错误,返回主界面')
                    return
            except Exception as e:
                print(e)
        else:
            print('请先登录')
            self.login()

    def signin(self):
        '''注册注意数据库保存'''
        print('注册账号')
        inname = input('请输入注册用户名：')
        inpassword = input('请输入注册密码:')
        try:
            sql = 'SELECT * FROM user WHERE name=%s'
            ret = self.cur.execute(sql, [inname, ])
            if ret:
                print('用户名已经存在')
                return
            sql_insert = 'INSERT INTO user VALUES(0, %s, %s)'
            ret1 = self.cur.execute(sql_insert, [inname, inpassword])
            if ret1:
                print('注册成功')
            self.connect_obj.commit()  # 提交

        except Exception as e:
            print(e)

    def change_password(self):
        '''注册注意数据库保存'''
        print('修改密码')
        old_password = input('请输入旧密码:')
        new_password = input('请输入新密码:')
        try:
            sql = 'SELECT * FROM user WHERE name=%s and password=%s'
            ret = self.cur.execute(sql, [self.login_name, old_password])
            if ret == 0:
                print('旧密码输入错误')
                return
            else:
                sql_update = 'UPDATE user SET password=%s WHERE name=%s'
                ret1 = self.cur.execute(sql_update, [new_password, self.login_name])
                if ret1:
                    print('修改成功')
                self.connect_obj.commit()  # 提交

        except Exception as e:
            print(e)


if __name__ == '__main__':
    sh = ShangHui()
    sh.printinfo()
