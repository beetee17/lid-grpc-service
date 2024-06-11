from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LanguageIdentificationRequest(_message.Message):
    __slots__ = ("audio_data",)
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    audio_data: bytes
    def __init__(self, audio_data: _Optional[bytes] = ...) -> None: ...

class LanguageIdentificationResponse(_message.Message):
    __slots__ = ("language_probabilities",)
    class LanguageProbabilitiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    LANGUAGE_PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    language_probabilities: _containers.ScalarMap[str, float]
    def __init__(self, language_probabilities: _Optional[_Mapping[str, float]] = ...) -> None: ...
