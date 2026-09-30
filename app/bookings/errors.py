from app.shared.errors import DomainError


class BookingNotFound(DomainError):
    pass


class BookingConflict(DomainError):
    pass


class InvalidBookingDates(DomainError):
    pass
