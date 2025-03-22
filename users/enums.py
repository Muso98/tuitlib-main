from enum import Enum


class UserType(Enum):
    librarian = 'librarian'
    professional = 'professional'
    student = 'student'
    other = 'other'

    @classmethod
    def choices(cls):
        return ((role.name, role.value) for role in cls)
