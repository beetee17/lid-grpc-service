from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LanguageIdentificationRequest(_message.Message):
    __slots__ = ("audio_data",)
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    audio_data: bytes
    def __init__(self, audio_data: _Optional[bytes] = ...) -> None: ...

class LanguageIdentificationResponse(_message.Message):
    __slots__ = ("language_code", "confidence")
    LANGUAGE_CODE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    language_code: str
    confidence: float
    def __init__(self, language_code: _Optional[str] = ..., confidence: _Optional[float] = ...) -> None: ...
