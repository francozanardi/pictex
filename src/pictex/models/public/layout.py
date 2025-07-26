from dataclasses import dataclass

@dataclass
class Margin:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

@dataclass
class Padding:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0
