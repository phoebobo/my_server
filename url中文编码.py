import urllib.parse as parse

# 这是编码
ret = parse.quote('后羿')
print(ret)

# 这是解码
unret = parse.unquote(ret)
print(unret)