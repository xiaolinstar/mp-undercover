from src.models.room import Room, RoomStatus
from src.models.user import User
from src.repositories.room_repository import RoomRepository
from src.repositories.user_repository import UserRepository
from src.services.game_service import GameService


class DummyRepo:
    def __init__(self):
        self.rooms = {}
        self.users = {}
    def exists(self, rid):
        return rid in self.rooms
    def save_room(self, room):
        self.rooms[room.room_id] = room
        return True


class MockPush:
    def __init__(self):
        self.calls = []
    def enabled(self):
        return True
    def send_text(self, openid, content):
        self.calls.append((openid, content))
        return True
    def get_user_nickname(self, openid):
        return "昵称" + openid[-1]


def test_join_room_fill_nickname(monkeypatch):
    import fakeredis
    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    assert ok
    ok, msg = svc.join_room("u2", rid)
    u2 = user_repo.get("u2")
    assert u2.nickname.startswith("昵称")


def test_start_game_push_words(monkeypatch):
    import fakeredis
    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    svc.join_room("u2", rid)
    svc.join_room("u3", rid)
    ok, res = svc.start_game("u1")
    assert ok
    assert any("您的词语" in c for _, c in push.calls)


def test_vote_push_status(monkeypatch):
    import fakeredis
    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    svc.join_room("u2", rid)
    svc.join_room("u3", rid)
    svc.start_game("u1")
    push.calls.clear()
    svc.vote_player("u1", 2)
    assert any("房间状态" in c for _, c in push.calls)

