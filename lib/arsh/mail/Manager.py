# -*- coding: utf-8 -*-
__docformat__ = 'reStructuredText'



class DecoratorManager():
    _instance = None

    def __init__(self):
        self._fs = {}


    @staticmethod
    def get():
        """
        :rtype Manager
        :return:singleton manager
        """
        if DecoratorManager._instance is None:
            DecoratorManager._instance = DecoratorManager()
            return DecoratorManager._instance
        return DecoratorManager._instance


    def activate_hook(self, name, object_model, *args):
        """if a function with key==name exist then call that function
        :type name: str
        :type object_model: object
        :param name: name of hook
        :param object_model: شی مدلی که تابع‌های صدا شده به وسیله‌ی آن اعمال مورد نظرشان را انجام می‌دهند.
        :param args: extra arguments passed to function
        :return: result of function call
        """
        functions = self._fs.get(name, [])
        for function in functions:
            function(object_model, *args)


    def register(self, hook_name, function):
        """append {'hook_name':function} to Decorator
        :type hook_name: str
        :type function: callable
        :param hook_name: name of hook
        :param function: function
        :return: None
        """
        if not hasattr(function, '__call__'):
            raise ValueError('Registered function must be callable')
        if not self._fs.get(hook_name, None):
            self._fs[hook_name] = []
        if not function in self._fs[hook_name]:
            self._fs[hook_name].append(function)
