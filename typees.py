

class BaseStation():
    def __init__(self, index: int, serial: str, matrix=None):
        self.index = index
        self.serial = serial
        self.matrix = matrix

    def __repr__(self) -> str:
        return f"index: {self.index}\nserial: {self.serial}\n"


