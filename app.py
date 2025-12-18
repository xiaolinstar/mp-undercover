from flask import Flask, request
import hashlib
import os
import xml.etree.ElementTree as ET
import time
import random
import redis
import json

app = Flask(__name__)

# 微信公众号的token，可以从环境变量获取或者硬编码
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'your_wechat_token_here')  # 请替换为实际的token

# Redis连接
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(REDIS_URL)

# 游戏词汇库
WORDS = {
    "水果类": [
        ("苹果", "香蕉"),
        ("西瓜", "冬瓜"),
        ("草莓", "樱桃"),
        ("橙子", "橘子"),
        ("葡萄", "提子")
    ],
    "动物类": [
        ("老虎", "狮子"),
        ("大象", "犀牛"),
        ("猴子", "猩猩"),
        ("企鹅", "海豚"),
        ("熊猫", "树袋熊")
    ],
    "生活用品类": [
        ("牙刷", "梳子"),
        ("雨伞", "雨衣"),
        ("手机", "电脑"),
        ("钱包", "背包"),
        ("眼镜", "墨镜")
    ]
}


@app.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello World!'


@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200


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


@app.route('/', methods=['POST'])
def wechat_response():
    """
    处理微信公众号的消息推送
    """
    try:
        # 解析XML消息
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        # 提取消息信息
        to_user = root.find('ToUserName').text
        from_user = root.find('FromUserName').text
        msg_type = root.find('MsgType').text
        create_time = root.find('CreateTime').text
        
        # 初始化响应内容
        response_content = ""
        
        if msg_type == 'text':
            content = root.find('Content').text
            response_content = handle_text_message(from_user, content)
        elif msg_type == 'event':
            event = root.find('Event').text
            if event == 'subscribe':
                response_content = "欢迎关注！请输入'创建房间'来创建一个新的谁是卧底游戏房间，或输入'加入房间+房间号'来加入现有房间。"
            else:
                response_content = "暂不支持此事件类型"
        else:
            response_content = "暂不支持此消息类型"
        
        # 构造响应XML
        response_xml = f"""
        <xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{response_content}]]></Content>
        </xml>
        """
        
        return response_xml
    except Exception as e:
        app.logger.error(f'Wechat message processing error: {e}')
        return 'success'  # 微信服务器要求即使出错也要返回success


def handle_text_message(user_id, content):
    """
    处理文本消息
    """
    content = content.strip()
    
    # 处理用户命令
    if content == '创建房间':
        return create_room(user_id)
    elif content.startswith('加入房间'):
        room_id = content[4:].strip()  # 去掉"加入房间"前缀
        return join_room(user_id, room_id)
    elif content == '开始游戏':
        return start_game(user_id)
    elif content == '查看状态':
        return show_status(user_id)
    elif content.startswith('投票'):
        target = content[3:].strip()  # 去掉"投票"前缀
        return handle_vote(user_id, target)
    elif content == '帮助':
        return show_help()
    else:
        return "未知命令，请输入'帮助'查看可用命令"


def create_room(user_id):
    """
    创建新房间
    """
    # 生成4位随机房间号
    room_id = str(random.randint(1000, 9999))
    
    # 确保房间号唯一
    while get_room(room_id):
        room_id = str(random.randint(1000, 9999))
    
    # 创建房间
    room_data = {
        'room_id': room_id,
        'creator': user_id,
        'players': [user_id],
        'status': 'waiting',  # waiting, playing, ended
        'words': None,
        'undercovers': [],  # 多个卧底
        'current_round': 1,
        'eliminated': []
    }
    
    save_room(room_id, room_data)
    
    # 保存用户信息
    user_data = {
        'openid': user_id,
        'nickname': f'玩家1',
        'current_room': room_id
    }
    save_user(user_id, user_data)
    
    return f"房间创建成功！房间号：{room_id}\n请其他玩家输入'加入房间{room_id}'加入房间\n房主输入'开始游戏'即可开始游戏"


def join_room(user_id, room_id):
    """
    加入房间
    """
    # 检查房间是否存在
    room = get_room(room_id)
    if not room:
        return "房间不存在，请检查房间号"
    
    # 检查房间状态
    if room['status'] != 'waiting':
        return "游戏已经开始或结束，无法加入"
    
    # 检查是否已在房间中
    if user_id in room['players']:
        return "您已在房间中"
    
    # 加入房间
    room['players'].append(user_id)
    save_room(room_id, room)
    
    # 保存用户信息
    user_data = {
        'openid': user_id,
        'nickname': f'玩家{len(room["players"])}',
        'current_room': room_id
    }
    save_user(user_id, user_data)
    
    # 通知房间内其他人有新玩家加入
    notify_players(room_id, f"新玩家加入房间，当前房间人数：{len(room['players'])}")
    
    return f"成功加入房间{room_id}！当前房间人数：{len(room['players'])}"


def start_game(user_id):
    """
    开始游戏
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return "您不在任何房间中"
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 检查是否为房主
    if room['creator'] != user_id:
        return "只有房主才能开始游戏"
    
    # 检查房间人数
    player_count = len(room['players'])
    if player_count < 3:
        return "至少需要3人才能开始游戏"
    
    # 更改房间状态
    room['status'] = 'playing'
    
    # 根据玩家数量确定卧底数量
    if player_count <= 5:
        undercover_count = 1
    elif player_count <= 8:
        undercover_count = 2
    else:
        undercover_count = 3
    
    # 随机选择卧底
    room['undercovers'] = random.sample(room['players'], undercover_count)
    
    # 随机选择词语类别和词语对
    category = random.choice(list(WORDS.keys()))
    word_pair = random.choice(WORDS[category])
    
    # 设置词语
    room['words'] = {
        'civilian': word_pair[0],  # 平民词
        'undercover': word_pair[1]  # 卧底词
    }
    
    save_room(room_id, room)
    
    # 通知所有玩家游戏开始和各自的词语
    for player in room['players']:
        if player in room['undercovers']:
            word = room['words']['undercover']
            role = "卧底"
        else:
            word = room['words']['civilian']
            role = "平民"
        
        send_message(player, f"游戏开始！\n词语类别：{category}\n您的身份：{role}\n您的词语：{word}\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负")
    
    # 特别提醒房主
    send_message(room['creator'], f"\n您是房主，请在线下游戏结束后，通过'投票 @某人'的方式来决定被淘汰的玩家")
    
    return "success"  # 对于发起者不需要回复


def handle_vote(user_id, target):
    """
    处理房主投票
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return "您不在任何房间中"
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 检查游戏状态
    if room['status'] != 'playing':
        return "游戏尚未开始或已结束"
    
    # 检查是否为房主
    if room['creator'] != user_id:
        return "只有房主才能进行投票"
    
    # 查找被投票的玩家
    target_player = None
    for player in room['players']:
        player_data = get_user(player)
        if player_data and target in player_data.get('nickname', ''):
            target_player = player
            break
    
    if not target_player:
        return "未找到该玩家，请确认玩家昵称"
    
    # 记录被淘汰的玩家
    room['eliminated'].append(target_player)
    save_room(room_id, room)
    
    # 通知结果
    target_data = get_user(target_player)
    target_nickname = target_data['nickname'] if target_data else f'玩家{room["players"].index(target_player)+1}'
    notify_players(room_id, f"房主投票决定：{target_nickname}被淘汰")
    
    # 检查游戏是否结束
    check_game_end(room_id)
    
    return "success"


def check_game_end(room_id):
    """
    检查游戏是否结束
    """
    room = get_room(room_id)
    
    # 检查是否有卧底被淘汰
    eliminated_undercovers = set(room['undercovers']) & set(room['eliminated'])
    
    # 如果所有卧底都被淘汰，平民获胜
    if len(eliminated_undercovers) == len(room['undercovers']):
        room['status'] = 'ended'
        save_room(room_id, room)
        notify_players(room_id, "游戏结束！平民获胜，成功找出了所有卧底！")
        return
    
    # 检查剩余玩家数量
    remaining_players = [player for player in room['players'] if player not in room['eliminated']]
    
    # 如果剩余玩家中卧底数量大于等于平民数量，则卧底获胜
    remaining_undercovers = set(room['undercovers']) & set(remaining_players)
    remaining_civilians = set(remaining_players) - set(remaining_undercovers)
    
    if len(remaining_undercovers) >= len(remaining_civilians):
        room['status'] = 'ended'
        save_room(room_id, room)
        notify_players(room_id, "游戏结束！卧底获胜！")
        return
    
    # 游戏继续，进入下一轮
    room['current_round'] += 1
    save_room(room_id, room)
    
    # 通知进入下一轮
    notify_players(room_id, f"进入第{room['current_round']}轮，请继续线下进行游戏")


def show_status(user_id):
    """
    显示当前状态
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return "您不在任何房间中"
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    status_text = f"房间号：{room_id}\n房间状态：{room['status']}\n房间成员："
    
    for i, player in enumerate(room['players']):
        player_data = get_user(player)
        nickname = player_data['nickname'] if player_data else f'玩家{i+1}'
        if player == room['creator']:
            nickname += "(房主)"
        if player in room.get('undercovers', []):
            nickname += "(卧底)"
        if player in room.get('eliminated', []):
            nickname += "(已淘汰)"
        status_text += f"\n{i+1}. {nickname}"
    
    if room['status'] == 'playing':
        status_text += f"\n\n当前轮次：第{room['current_round']}轮"
        status_text += f"\n卧底人数：{len(room.get('undercovers', []))}"
        status_text += f"\n已淘汰：{len(room.get('eliminated', []))}人"
    
    return status_text


def show_help():
    """
    显示帮助信息
    """
    help_text = """谁是卧底游戏命令：
1. 创建房间 - 创建新的游戏房间
2. 加入房间+房间号 - 加入指定房间（例如：加入房间1234）
3. 开始游戏 - 房主开始游戏（至少3人）
4. 查看状态 - 查看当前房间状态
5. 投票 @某人 - 房主投票给指定玩家（游戏结束后决定胜负）
6. 帮助 - 显示此帮助信息"""
    return help_text


def notify_players(room_id, message, exclude=None):
    """
    通知房间内的所有玩家
    """
    room = get_room(room_id)
    for player in room['players']:
        if player != exclude:
            send_message(player, message)


def send_message(user_id, message):
    """
    发送消息给指定用户（模拟实现）
    在实际应用中，这里需要调用微信API发送客服消息
    """
    print(f"发送给 {user_id} 的消息: {message}")


def get_room(room_id):
    """
    从Redis获取房间信息
    """
    try:
        room_data = redis_client.get(f"room:{room_id}")
        if room_data:
            return json.loads(room_data)
        return None
    except Exception as e:
        app.logger.error(f"Error getting room {room_id}: {e}")
        return None


def save_room(room_id, room_data):
    """
    将房间信息保存到Redis
    """
    try:
        redis_client.set(f"room:{room_id}", json.dumps(room_data))
    except Exception as e:
        app.logger.error(f"Error saving room {room_id}: {e}")


def get_user(user_id):
    """
    从Redis获取用户信息
    """
    try:
        user_data = redis_client.get(f"user:{user_id}")
        if user_data:
            return json.loads(user_data)
        return None
    except Exception as e:
        app.logger.error(f"Error getting user {user_id}: {e}")
        return None


def save_user(user_id, user_data):
    """
    将用户信息保存到Redis
    """
    try:
        redis_client.set(f"user:{user_id}", json.dumps(user_data))
    except Exception as e:
        app.logger.error(f"Error saving user {user_id}: {e}")


if __name__ == '__main__':
    app.run()