from typing import TypeVar, Generic

T = TypeVar("T")

class StyleProperty(Generic[T]):
    def __init__(self, default: T, inheritable: bool = True):
        self._value = default
        self._default = default
        self._inheritable = inheritable
        self._was_set = False

    @property
    def was_set(self):
        return self._was_set

    @property
    def is_inheritable(self) -> bool:
        return self._inheritable

    def get(self) -> T:
        """
        Returns the wrapped value.
        IMPORTANT: the returned value mustn't be used to set its internal state. You must set the internal state calling set().
        For example, if get() returns a list, you can't modify the returned list internal state directly,
        you must create a new instance and call set() with the new value.
        """
        return self._value

    def set(self, new_value: T):
        self._value = new_value
        self._was_set = True

    def reset(self):
        self._value = self._default
        self._was_set = False

    def __call__(self) -> T:
        return self._value

    def __repr__(self):
        return f"{self._value} (set={self._was_set}, inheritable={self._inheritable})"

    def __eq__(self, other):
        return self._value == other
