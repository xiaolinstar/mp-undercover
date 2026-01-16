from wechatpy import WeChatClient as BaseWeChatClient
from wechatpy.session.redisstorage import RedisStorage
from redis import Redis

class WeChatClient:
    def __init__(self, app_id: str, app_secret: str, redis_client: Redis = None):
        if redis_client:
            session_interface = RedisStorage(redis_client, prefix="wechatpy")
            self.client = BaseWeChatClient(app_id, app_secret, session=session_interface)
        else:
            self.client = BaseWeChatClient(app_id, app_secret)

    def send_text(self, openid: str, content: str) -> bool:
        try:
            self.client.message.send_text(openid, content)
            return True
        except Exception:
            return False

    def get_user_nickname(self, openid: str) -> str:
        try:
            user_info = self.client.user.get(openid)
            return user_info.get("nickname", "")
        except Exception:
            return ""
