# coding=utf-8
""" Session store for Tornado + Redis
    assumptions:
    - using tornado + redis
    - using Python 2.7+
"""
import cPickle as pickle
from uuid import uuid4
import time


class RedisSessionStore:
    def __init__(self, redis_connection, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
        }
        self.options.update(options)
        self.redis = redis_connection

    def prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    @staticmethod
    def generate_sid():
        return uuid4().get_hex()

    def get_session(self, sid, name):
        data = self.redis.hget(self.prefixed(sid), name)
        session = pickle.loads(data) if data else dict()
        return session

    def set_session(self, sid, session_data, name):
        expiry = self.options['expire']
        self.redis.hset(self.prefixed(sid), name, pickle.dumps(session_data))
        if expiry:
            self.redis.expire(self.prefixed(sid), expiry)

    def delete_session(self, sid):
        self.redis.delete(self.prefixed(sid))


class Session:
    def __init__(self, session_store, session_id=None):
        self._store = session_store
        self._session_id = session_id if session_id else self._store.generate_sid()
        self._session_data = self._store.get_session(self._session_id, 'data')
        self.dirty = False

    def clear(self):
        self._store.delete_session(self._session_id)

    def access(self, remote_ip):
        access_info = {'remote_ip': remote_ip, 'time': '%.6f' % time.time()}
        self._store.set_session(
            self._session_id,
            'last_access',
            pickle.dumps(access_info)
        )

    def last_access(self):
        access_info = self._store.get_session(self._session_id, 'last_access')
        return pickle.loads(access_info)

    @property
    def session_id(self):
        return self._session_id

    def __getitem__(self, key):
        return self._session_data[key]

    def __setitem__(self, key, value):
        self._session_data[key] = value
        self._dirty()

    def __delitem__(self, key):
        del self._session_data[key]
        self._dirty()

    def __len__(self):
        return len(self._session_data)

    def __contains__(self, key):
        return key in self._session_data

    def __iter__(self):
        for key in self._session_data:
            yield key

    def __repr__(self):
        return self._session_data.__repr__()

    def __del__(self):
        if self.dirty:
            self._save()

    def _dirty(self):
        self.dirty = True

    def _save(self):
        self._store.set_session(self._session_id, self._session_data, 'data')
        self.dirty = False