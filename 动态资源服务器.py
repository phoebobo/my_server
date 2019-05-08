import gevent
from gevent import monkey
import sys
import socket
import chardet

'''这个程序实现的是一个动态资源服务器'''
gevent.monkey.patch_all()  # 给所有耗时操作打补丁


class Server(object):
    def __init__(self, port, app):
        '''初始化，实现逻辑'''
        self.app = app
        # 创建服务器的套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', port))
        self.response_data = None  # 这个是响应报文的数据（除了响应体之外）

    def start(self):
        # 服务器开始运行
        self.server_socket.listen()
        while True:
            handler_socket, address = self.server_socket.accept()
            # handler_prc = threading.Thread(
            #     target=self.handler_client, args=(handler_socket,))
            # handler_prc.start()
            gv = gevent.spawn(self.handler_client, handler_socket)
            gv.join()

    def start_response(self, status, header_list):
        '''
        这个函数实现的是拼接响应报文，遵循的还是响应报文的格式，请求动态资源调用
        :param status: 状态码，例如'200 ok'
        :param header_list: 列表 例如[(server,wsgisever),(name,xiaoming)]
        :return:
        HTTP/1.1 状态码 说明\r\n
        Headername1:header_value\r\n
        Headername2:header_value\r\n
        Headername3:header_value\r\n
        \r\n
        Response_body 响应体，就是数据，网页、图片、文本
        '''
        response_header_firstline = 'HTTP/1.1 %s\r\n' % status
        response_header = ''
        # 这是键值 直接拆包
        for header_key, header_value in header_list:
            response_header += ('%s:%s\r\n' % (header_key, header_value))
        self.response_data = response_header_firstline + response_header + '\r\n'

    def handler_client(self, handler_socket):
        # 人工客服处理客户端的请求
        data = handler_socket.recv(1024).decode('utf-8')  # 字节流文件--字符串
        request_datas_list = data.split('\r\n')
        for obj in request_datas_list:
            print(obj)
        # todo:开始拼接的响应报文
        # todo:截取请求的路径，获取请求的内容，根据路径不同返回不同数据

        first_line = request_datas_list[0]

        # ret = re.search('GET (/.*?) HTTP/1.1', first_line) #这个是正则
        # 获取第一行，然后路径
        firstline_list = first_line.split(' ')
        # 判断是否有ret值，如果没有，说明是一个非法请求
        if not firstline_list:
            handler_socket.close()
            return
        # 尝试没有就给他一个默认值
        try:
            request_path = firstline_list[1]
        except BaseException:
            request_path = '/'
        # request_path = ret.group(1)

        print('**********************')

        '''
        HTTP/1.1 状态码 说明\r\n
        Headername1:header_value\r\n
        Headername2:header_value\r\n
        Headername3:header_value\r\n
        \r\n
        Response_body 响应体，就是数据，网页、图片、文本
        '''

        environ = {'path': request_path}
        if request_path.endswith('.py'):
            # 交给动态资源处理框架取处理
            print('此时进入动态资源处理')

            user_info = request_datas_list[len(request_datas_list)-1]
            responsebody = self.app(environ, self.start_response, user_info)
            data = self.response_data + responsebody
            handler_socket.send(data.encode('UTF-8'))
            handler_socket.close()
        else:
            # 这里交给静态资源处理
            if request_path == '/':
                status_code = '200 ok'
                responsebody = 'hello world!'
                # 暂时不写静态
#             elif request_path == '/index.html':
#                 status_code = '200 ok'
#                 with open('index.html') as f:
#                     response_data = f.read()
#                 responsebody = response_data
#             elif request_path == '/login.html':
#                 status_code = '200 ok'
#                 with open('login.html') as f:
#                     responsebody = f.read()%('这是登录页面', '''<form method="post" action="signin.py">
#     <input type="submit" value="跳转注册">
# </form>''')

            else:
                status_code = '404 not found'
                with open('err.html') as f:
                    responsebody = f.read()
            responseHeader = 'HTTP/1.1' + status_code + ' 123\r\n'
            responseHeader += '\r\n'
            # 判断responsebody是否是二进制文件
            # 需要知道发送数据大小，已经发送了多少
            try:
                chardet.detect(responsebody)
                sent_count = 0  # 已经发送数据大小
                reponse = responseHeader.encode('utf-8') + responsebody
                while sent_count < len(reponse):
                    # send_size = int(sent_count + len(reponse) / 2)  # 一次发送数据大小加上当前位置
                    # 现在发送的数据大小
                    now_size = handler_socket.send(
                        reponse[sent_count:])
                    sent_count += now_size
                # handler_socket.send(
                #     responseHeader.encode('utf-8') + responsebody)
            except BaseException:
                reponse = responseHeader + responsebody
                sent_count = 0  # 已经发送数据大小
                while sent_count < len(reponse):
                    # send_size = int(sent_count + len(reponse) / 2)  # 一次发送数据大小加上当前位置
                    # 现在发送的数据大小
                    now_size = handler_socket.send(
                        reponse[sent_count:].encode('utf-8'))  # send有可能发送不完
                    sent_count += now_size

                # ret = handler_socket.send(reponse.encode('utf-8'))
                # print(ret)
            finally:
                # 最后关闭
                handler_socket.close()


def main():
    '''实现主要逻辑'''
    try:
        port = sys.argv[1]
        frame_name = sys.argv[2]  # 用来表示哪个框架的哪个接口
    except:
        # 获取不到参数则给定默认参数
        print('参数缺少，使用默认参数端口为5000')
        port = 5000
        frame_name = 'application:app'
        return
    finally:
        # 获取接口名字切分，获取的是一个列表
        frame_list = frame_name.split(':')
        modle_name = frame_list[0]
        func_name = frame_list[1]
        # 这是新的一种导包方式
        # app是指接口的导用
        # __import__的参数是字符串，文件名
        frame_obj = __import__(modle_name)
        app = getattr(frame_obj, func_name)
        # 初始化我的服务器
        my_server = Server(port=int(port), app=app)
        gv = gevent.spawn(my_server.start())  # 这个添加函数
        gv.join()

if __name__ == '__main__':
    main()
