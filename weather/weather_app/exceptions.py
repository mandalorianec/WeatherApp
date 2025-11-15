class ApiException(Exception):
    def __init__(self, message="Что-то пошло не так", code=500):
        self.message = message
        self.code = code

class EmptySearchException(ApiException):
    def __init__(self):
        super().__init__("Пустой поисковой запрос", 400)


class ApiAuthenticationError(ApiException):
    def __init__(self):
        super().__init__("Проблемы с API ключом", 401)


class RateLimitExceededError(ApiException):
    def __init__(self):
        super().__init__("Превышен лимит запросов", 429)


class WebError(ApiException):
    def __init__(self):
        self.code = 503
        self.message = "Возникли проблемы с запросом"
