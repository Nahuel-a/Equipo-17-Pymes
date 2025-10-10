from enum import Enum



class RoleUser(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class StatusCredit(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"