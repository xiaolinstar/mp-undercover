from flask import Flask, request
import hashlib
import os

app = Flask(__name__)

# 微信公众号的token，可以从环境变量获取或者硬编码
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'your_wechat_token_here')  # 请替换为实际的token


@app.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello World!'


@app.route('/', methods=['GET'])
def wechat_verify():
    """
    处理微信公众号的signature检验
    根据微信文档：https://developers.weixin.qq.com/doc/subscription/guide/dev/push/
    """
    try:
        # 获取微信服务器发送的参数
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        if not all([signature, timestamp, nonce, echostr]):
            return 'Missing parameters', 400
        
        # 将token、timestamp、nonce按字典序排序
        sorted_list = sorted([WECHAT_TOKEN, timestamp, nonce])
        
        # 将排序后的三个字符串拼接成一个字符串
        combined_str = ''.join(sorted_list)
        
        # 对拼接后的字符串进行sha1加密
        sha1 = hashlib.sha1()
        sha1.update(combined_str.encode('utf-8'))
        encrypted_str = sha1.hexdigest()
        
        # 将加密后的字符串与signature比较
        if encrypted_str == signature:
            return echostr  # 验证成功，返回echostr
        else:
            return 'Invalid signature', 403
    except Exception as e:
        app.logger.error(f'Wechat verification error: {e}')
        return 'Internal server error', 500


if __name__ == '__main__':
    app.run()