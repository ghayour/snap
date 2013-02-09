# -*- coding: utf-8 -*-

class Singleton(object):
    _instance = None

    @classmethod
    def prepare(cls):
        """
            :return: Singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
