class SingletonMeta(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls._instance.get(cls) is None:
            cls._instance[cls] = super().__call__(*args, **kwargs)
        return cls._instance[cls]


class SingletonClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
