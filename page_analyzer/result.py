class Result:
    def __init__(self, is_ok=True, error_code=0, value=None):
        self.is_ok = is_ok
        self.error_code = error_code
        self.value = value

        