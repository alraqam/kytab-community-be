from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class NotificationNotFoundError(NotFound):
    pass

class IsNotNotificationOwnerError(Forbidden):
    pass

class NotificationPreferenceNotFoundError(NotFound):
    pass

class IsNotNotificationPreferenceOwnerError(Forbidden):
    pass

class NotificationPreferenceAlreadyExistsError(Conflict):
    pass
