from app.shared.errors import DomainError


class RoomNotFound(DomainError):
    pass


class RoomCapacityExceeded(DomainError):
    pass


class InvalidSearchDates(DomainError):
    pass


class UnknownAmenities(DomainError):
    def __init__(self, amenity_ids: list[int]) -> None:
        self.amenity_ids = sorted(set(amenity_ids))
        super().__init__()
