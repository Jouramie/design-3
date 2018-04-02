from enum import Enum


class Target(Enum):

    WHEELS = 0x33
    ROTATE = 0x20


class Direction(Enum):

    LEFT = 0x11
    FORWARD = 0xff
    RIGHT = 0x22
    BACKWARD = 0xbb


class Command(Enum):

    GRAB_CUBE = bytearray(b'\x6c\x12\x23')
    DROP_CUBE = bytearray(b'\xdc\x12\x23')
    CAN_GRAB_CUBE = bytearray(b'\xc4\x12\x34')
    THE_END = bytearray(b'\xee\x12\x34')

    SEND_AGAIN = bytearray(b'\x46\x41\x12')