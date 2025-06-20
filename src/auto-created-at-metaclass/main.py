import datetime
import time


class AddCreatedAtMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.datetime.now()
        return super().__new__(cls, name, bases, attrs)


if __name__ == "__main__":

    class TestClass(metaclass=AddCreatedAtMeta):
        pass

    obj1 = TestClass()
    assert hasattr(obj1, "created_at"), "Атрибут created_at не добавлен"
    assert isinstance(obj1.created_at, datetime.datetime), (
        "created_at не является datetime"
    )

    time.sleep(0.1)

    class AnotherTestClass(metaclass=AddCreatedAtMeta):
        pass

    obj2 = AnotherTestClass()
    assert obj1.created_at != obj2.created_at, "Время создания должно отличаться"

    class ChildTestClass(TestClass):
        pass

    obj3 = ChildTestClass()
    assert hasattr(obj3, "created_at"), "Атрибут created_at не унаследован"
