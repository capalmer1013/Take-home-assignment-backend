class BadRequestError(Exception):
    def __init__(self, error):
        self.error = error
        self.status_code = 400


# Make all other exceptions inherit from BadRequestError


class AuthenticationError(BadRequestError):
    def __init__(self, error):
        self.error = error
        self.status_code = 401


class AuthorizationError(BadRequestError):
    def __init__(self, error):
        self.error = error
        self.status_code = 403
