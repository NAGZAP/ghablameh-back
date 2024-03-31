from django.core.exceptions import ValidationError

def validate_file_size(file):
    MAX_SIZE_KB = 900

    if file.size>MAX_SIZE_KB * 1024:
        raise ValidationError(f"عکس انتخابی باید کمتر از  {MAX_SIZE_KB}kb باشد")