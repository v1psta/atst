from uuid import uuid4
import json
from redis import exceptions


class SessionStorageError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


class Sessions(object):
    def start_session(self, user):
        raise NotImplementedError()

    def get_session(self, session_id):
        raise NotImplementedError()

    def generate_session_id(self):
        return str(uuid4())

    def build_session_dict(self, user=None):
        return {"user": user or {}}


class DictSessions(Sessions):
    def __init__(self):
        self.sessions = {}

    def start_session(self, user):
        session_id = self.generate_session_id()
        self.sessions[session_id] = self.build_session_dict(user=user)
        return session_id

    def get_session(self, session_id):
        try:
            session = self.sessions[session_id]
        except KeyError:
            raise SessionNotFoundError

        return session


class RedisSessions(Sessions):
    def __init__(self, redis, ttl_seconds):
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    def start_session(self, user):
        session_id = self.generate_session_id()
        session_dict = self.build_session_dict(user=user)
        session_serialized = json.dumps(session_dict)
        try:
            self.redis.setex(session_id, self.ttl_seconds, session_serialized)
        except exceptions.ConnectionError:
            raise SessionStorageError
        return session_id

    def get_session(self, session_id):
        try:
            session_serialized = self.redis.get(session_id)
        except exceptions.ConnectionError:
            raise

        if session_serialized:
            self.redis.expire(session_id, self.ttl_seconds)
            return json.loads(session_serialized)
        else:
            raise SessionNotFoundError
