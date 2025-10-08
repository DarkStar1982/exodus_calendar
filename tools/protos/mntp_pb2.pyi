from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MNTP_Packet(_message.Message):
    __slots__ = ("Header", "RootDelay", "Dispersion", "ReferenceID", "ReferenceTimestamp", "OriginTimestamp", "ReceiveTimestamp", "TransmitTimestamp", "SHA2Checksum")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ROOTDELAY_FIELD_NUMBER: _ClassVar[int]
    DISPERSION_FIELD_NUMBER: _ClassVar[int]
    REFERENCEID_FIELD_NUMBER: _ClassVar[int]
    REFERENCETIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ORIGINTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RECEIVETIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TRANSMITTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SHA2CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    Header: int
    RootDelay: int
    Dispersion: int
    ReferenceID: int
    ReferenceTimestamp: int
    OriginTimestamp: int
    ReceiveTimestamp: int
    TransmitTimestamp: int
    SHA2Checksum: str
    def __init__(self, Header: _Optional[int] = ..., RootDelay: _Optional[int] = ..., Dispersion: _Optional[int] = ..., ReferenceID: _Optional[int] = ..., ReferenceTimestamp: _Optional[int] = ..., OriginTimestamp: _Optional[int] = ..., ReceiveTimestamp: _Optional[int] = ..., TransmitTimestamp: _Optional[int] = ..., SHA2Checksum: _Optional[str] = ...) -> None: ...
