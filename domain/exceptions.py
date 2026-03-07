class DomainException(Exception):
    pass


class EntityNotFoundException(DomainException):
    pass


class UnauthorizedException(DomainException):
    pass


class BudgetExceededException(DomainException):
    pass


class ValidationException(DomainException):
    pass
