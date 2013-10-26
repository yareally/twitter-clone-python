# coding=utf-8
""" Session store for Tornado + Redis
    assumptions:
    - using tornado + redis
    - using Python 2.7+
"""

# deal with < Python 3.3 where cPickle was not merged
try:
    import cPickle as pickle
except ImportError:
    import pickle

from uuid import uuid4
import time

class RedisSessionStore(object):
    """

    @param redis_connection:
    @type redis_connection: StrictRedis
    @param options:
    @type options: dict
    """

    def __init__(self, redis_connection, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
        }
        self.options.update(options)
        self.redis = redis_connection

    def prefix(self, sid):
        """

        @param sid:
        @type sid: str
        @return:
        @rtype: str
        """
        return '%s:%s' % (self.options['key_prefix'], sid)

    @staticmethod
    def gen_sid():
        """


        @return:
        @rtype: str
        """
        return uuid4().get_hex()

    def get_session(self, sid, name):
        """
        Get the session object
        @param sid:
        @type sid: str
        @param name:
        @type name: str
        @return:
        @rtype: dict
        """
        data = self.redis.hget(self.prefix(sid), name)
        session = pickle.loads(data) if data else dict()
        return session

    def set_session(self, sid, session_data, name):
        """
        Set the session object

        @param sid:
        @type sid: string
        @param session_data:
        @type session_data: dict
        @param name:
        @type name: str
        """
        expiry = self.options['expire']
        self.redis.hset(self.prefix(sid), name, pickle.dumps(session_data))
        if expiry:
            self.redis.expire(self.prefix(sid), expiry)

    def delete_session(self, sid):
        """

        @param sid:
        @type sid: str
        """
        self.redis.delete(self.prefix(sid))


class Session(object):
    """

    @param session_store:
    @type session_store: RedisSessionStore
    @param session_id:
    @type session_id: str
    """

    def __init__(self, session_store, session_id=None):
        self._store = session_store
        self._session_id = session_id if session_id else self._store.gen_sid()
        self._session_data = self._store.get_session(self._session_id, 'data')
        self.dirty = False

    def clear(self):
        """
        Deletes the current session
        """
        self._store.delete_session(self._session_id)

    def access(self, remote_ip):
        """

        @param remote_ip:
        @type remote_ip: str
        """
        access_info = {'remote_ip': remote_ip, 'time': '%.6f' % time.time()}
        self._store.set_session(
            self._session_id,
            pickle.dumps(access_info),
            'last_access'
        )

    def last_access(self):
        """


        @return:
        @rtype: dict
        """
        access_info = self._store.get_session(self._session_id, 'last_access')
        return pickle.loads(access_info)

    @property
    def session_id(self):
        """


        @return:
        @rtype: str
        """
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