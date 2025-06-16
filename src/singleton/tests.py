import unittest

from .main import SingletonClass, SingletonMeta


class TestSingleton(unittest.TestCase):

    def test_metaclass_singleton(self):
        class TestClass(metaclass=SingletonMeta):
            def __init__(self, value):
                self.value = value

        instance_1 = TestClass(1)
        instance_2 = TestClass(2)

        self.assertIs(instance_1, instance_2)

    def test_new_method_singleton(self):
        class TestClass(SingletonClass):
            def __init__(self, value):
                self.value = value

        instance_1 = TestClass(1)
        instance_2 = TestClass(2)

        self.assertIs(instance_1, instance_2)


    def test_module_singleton(self):
        from .singleton_module import singleton_instance as instance_1
        from .singleton_module import singleton_instance as instance_2

        self.assertIs(instance_1, instance_2)


if __name__ == "__main__":
    unittest.main()
