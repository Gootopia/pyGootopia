# baseclass test

class BaseClass:
    message = 'base class'
    instances = 0

    def __init__(self):
        self.instances = self.instances + 1
        self.myprint(self.instances)
        pass

    def myprint(self, text):
        print(text)

    @classmethod
    def method1(cls, text):
        print(text+"_CLASSMETHOD")


class DerivedClass(BaseClass):
    def __init__(self):
        self.myprint(self.instances)
        pass