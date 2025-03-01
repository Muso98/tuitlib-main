from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_isbn(value):
    clean_isbn = ''.join(c for c in value if c.isdigit() or c == 'X')
    if len(clean_isbn) != 10 and len(clean_isbn) != 13:
        raise ValidationError(_('Invalid ISBN format'))

    total = 0
    if len(clean_isbn) == 10:
        for i, digit in enumerate(clean_isbn):
            if digit == 'X':
                digit = 10
            total += int(digit) * (10 - i)
        if total % 11 != 0:
            raise ValidationError(_('Invalid ISBN-10'))
    elif len(clean_isbn) == 13:
        for i, digit in enumerate(clean_isbn):
            weight = 1 if i % 2 == 0 else 3
            total += int(digit) * weight
        if total % 10 != 0:
            raise ValidationError(_('Invalid ISBN-13'))

