from shopping import ShangHui

'''这是装饰器工厂函数来实现 类似于flask'''
# 定义一个路径字典
urlfuncdict = {}
# shsp尚汇优品对象
shsp = None
# 用户信息包括名字和密码
userinfo = None
# 验证是否登录
is_login = False
# 登陆后的账户名
user_name = ''
# 订单的货物信息
order_info = None

def route(url):
    # 装饰器工厂函数
    def wrapper(func):
        # 添加键值对，key是路径，value是函数的引用
        urlfuncdict[url] = func

        def inner():
            response_body = func()
            return response_body
        return inner
    return wrapper


@route('/signin.py')
def signin():
    with open('signin.html') as f:
        return f.read()


@route('/handler.py')
def handler():
    # 用来处理登录,返回的是布尔值
    if shsp.login(user_info=userinfo):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<h3>登录成功，按确认按钮跳转主页</h3><br>
<form method="post" action="index.py">
    <input type="submit" value="确认">
</form>
</body>
</html>'''
        global is_login, user_name
        user_name = shsp.login_name
        is_login = True
        print('登陆后保存的：',user_name,is_login)
    else:
        html = '''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
        <h3>账号密码错误，请重新登录</h3><br>
        <form method="post" action="login.py">
            <input type="submit" value="重新登录">
        </form>
        </body>
        </html>'''

    return html


@route('/change_psd.py')
def change_psd():
    # 用来修改密码
    with open('change_psd.html') as f:
        return f.read()


@route('/login.py')
def login():
    with open('login.html') as f:
        html_str = f.read()
    # 判断是否注册后进入这个界面
    if 'reg' in userinfo:
        # 这是注册方法，返回布尔值判断注册成功与否
        print('注册账号', userinfo)
        if shsp.signin(user_info=userinfo):
            html = html_str % ('注册成功请输入账号密码登录', '')
        else:
            html = html_str % ('注册失败，名字已存在请重试', '''<form method="post" action="signin.py">
                <input type="submit" value="跳转注册">
            </form>''')
    elif 'old' in userinfo:
        # 这是修改密码方法,返回布尔值
        print('修改密码', userinfo)
        if shsp.change_password(user_info=userinfo):
            html = html_str % ('修改密码成功请重新登录', '')
        else:
            html = html_str % ('修改密码失败,账号或密码是输入错误', '''<form method="post" action="change_psd.py">
    <input type="submit" value="再次修改密码">
</form>''')
    else:
        html = html_str % ('这是登录页面', '''<form method="post" action="signin.py">
    <input type="submit" value="跳转注册">
</form>''')
    return html


@route('/exit.py')
def exit():
    # 用来关闭所有东西
    global is_login
    is_login = False
    shsp.close()
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<h1>你已经退出商城，欢迎再来！</h1>
</body>
</html>'''
    return html


@route('/index.py')
def index():
    # 用来显示网页内容
    '''<form method="post" action="login.py">
    <input type="submit" value="跳转登录">
</form>'''
    with open('index.html') as f:
        str_html = f.read()
    print('验证是否登录：', is_login)
    if is_login:
        # 登录状态则添加两个按钮，退出和更改密码
        html = str_html % (shsp.get_data_str(), '''<form method="post" action="exit.py">
    <input type="submit" value="退出登录">
</form>''', '''<form method="post" action="change_psd.py">
    <input type="submit" value="修改密码">
</form>''')
    else:
        html = str_html % (shsp.get_data_str(), '''<form method="post" action="login.py">
    <input type="submit" value="跳转登录">
</form>''', '')

    return html


@route('/order.py')
def order_comm():
    # 这是实现下订单

    if is_login:
        if shsp.order_comm(order_info=userinfo):
            global order_info
            order_info = userinfo
            with open('order_comm.html') as f:
                str_html = f.read()
            html = str_html
        else:
            html = '''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Title</title>
            </head>
            <body>
            <h1>下单失败，检查输入的商品名字或数量是否出错</h1>
            <form method="post" action="index.py">
                <input type="submit" value="跳转主页面">
            </form>
            </body>
            </html>'''
    else :
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<h1>账号没登录，请登录</h1>
<form method="post" action="index.py">
    <input type="submit" value="跳转主页面">
</form>
</body>
</html>'''
    return html


@route('/confirm_order.py')
def confirm_order():
    shsp.confirm_order(add_info=userinfo, order_info=order_info, sys_name=user_name)
    html = '''<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Title</title>
                </head>
                <body>
                <h1>下单成功，确认返回主页面</h1>
                <form method="post" action="index.py">
                    <input type="submit" value="跳转主页面">
                </form>
                </body>
                </html>'''
    return html


@route('/check_order.py')
def check_order():
    # 展示订单
    # if is_login:
    #
    # else:
    #     print('没登录，请登录')
    '''<form method="post" action="check_order.py">
    <input type="submit" value="查看订单">
</form>'''
    pass


@route('/error.py')
def error():
    return '404 not found'


def app(environ, start_response, user_info):
    '''

    :param environ: 字典，传入的是请求头
    :param start_response: 这是方法
    :return: 返回网页内容
    '''
    request_path = environ['path']
    print('app方法：', user_info)
    # 根据上面字典判断
    staus_code = ''
    global shsp, userinfo
    shsp = ShangHui()
    userinfo = user_info

    # 判断方法
    try:
        func = urlfuncdict[request_path]
        staus_code = '200 ok'

    except BaseException:
        staus_code = '404 NOT FOUND'
        func = error
    finally:
        start_response(staus_code, [('name', 'paul'), ('age', '18')])
        return func()

