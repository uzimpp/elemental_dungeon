"""
Singleton class that ensures only one instance of a class exists
"""

class Singleton:
    """Singleton class that ensures only one instance of a class exists"""
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def get_instance(cls):
        """Get the instance of the class"""
        return cls._instances.get(cls)

    @classmethod
    def reset_instance(cls):
        """Reset the instance of the class"""
        if cls in cls._instances:
            del cls._instances[cls]

    @classmethod
    def is_instance(cls):
        """Check if the class has an instance"""
        return cls in cls._instances
