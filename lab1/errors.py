class ParseError(Exception):
    def __init__(self, message, pos, text):
        super().__init__(message)
        self.message = message
        self.pos = pos
        self.text = text

    def __str__(self):
        return "Ошибка! " + self.message
