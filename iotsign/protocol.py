import construct
import enum

from construct import Struct, Select, Const, PaddedString, Enum, GreedyRange, Switch, this, Byte, Optional, NullTerminated, Bytes, RepeatUntil, StopIf, Sequence,FocusedSeq, Peek, GreedyBytes, RestreamData, If, Error, IfThenElse, Terminated, Default

class ControlCode(enum.IntEnum):
    NULL = 0x00
    START_OF_HEADER = 0x01
    START_OF_TEXT = 0x02
    END_OF_TEXT = 0x03
    END_OF_TRANSMISSION = 0x04
    ESCAPE = 0x1b


class TypeCode(enum.IntEnum):
    RESPONSE = 0x30
    ALL_SIGNS = 0x3F

class CommandCode(enum.IntEnum):
    WRITE_TEXT = 0x41

class DisplayPosition(enum.IntEnum):
    MIDDLE_LINE = 0x20
    TOP_LINE = 0x22
    BOTTOM_LINE = 0x26
    FILL = 0x30
    LEFT = 0x31
    RIGHT = 0x32

class FileLabel(enum.IntEnum):
    PRIORITY = 0x30

    def is_valid_string_file(self):
        return self.value not in {0x30, 0x3f}

    def is_reserved_for_target_file(self):
        return self.value in {0x31, 0x32, 0x33, 0x34, 0x35}


def switch_via_enum(enum_cls, keyfunc):
    def _switch_via_enum(*args):
        key = keyfunc(*args)
        if isinstance(key, enum_cls):
            return key
        try:
            return enum_cls[key]
        except KeyError:
            return object()
    return _switch_via_enum

Command = Struct(
    command_code=Enum(Byte, CommandCode),
    data_field=Switch(
        switch_via_enum(CommandCode, this.command_code),
        {
            CommandCode.WRITE_TEXT: Struct(
                file_label=Default(
                    Enum(Byte, FileLabel),
                    FileLabel.PRIORITY.value,
                ),
                file=Struct(
                    mode=Default(
                        Optional(
                            Struct(
                                _esc=Const(b"\x1b"),
                                display_position=Default(
                                    Enum(Byte, DisplayPosition),
                                    DisplayPosition.FILL,
                                ),
                                mode_code=Byte,
                                special_specifier=Byte,
                            ),
                        ),
                        None,
                    ),
                    message=GreedyRange(
                        FocusedSeq(
                            "item",
                            "next" / Peek(Byte),
                            StopIf(lambda this: this.next in {0x03, 0x04}),
                            "item" / Byte,
                        ),
                    ),
                ),
            )
        },
        default=Const(b"\xee"),
    ),
)

# FramedCommand =

Message = Struct(
    _sync=Default(
        Select(
            GreedyRange(Const(b"\x00")),
            GreedyRange(Const(b"\x01")),
        ),
        [b"\x00"] * 5,
    ),
    _start_of_header=Const(b"\x01"),
    type_code=construct.Enum(
        Byte, TypeCode
    ),
    sign_address=PaddedString(length=2, encoding="ascii"),
    commands=GreedyRange(
        FocusedSeq(
            "framed_command",
            "_start_of_text" / Const(b"\x02"),
            "framed_command" / FocusedSeq(
                "command",
                "command" / Command,
            ),
            "_end_of_text" / Optional(Const(b"\x03")),
        )
    ),

    _end_of_transmission=Const(b"\x04"),
    _terminated=Terminated,
    # command=construct.Select(
        # construct.Struct(
            # code=construct.Const(CommandCode.WRITE_TEXT, subcon=construct.Byte),
        # ),
    # ),
)

# print(Message.parse(b'\x00\x00\x00\x00\x00\x01?00\x02\x41\x30anusss\x04'))

print((Message.build({
    "type_code": TypeCode.ALL_SIGNS,
    "sign_address": "00",
    "commands": [
        {
            "command_code": CommandCode.WRITE_TEXT,
            "data_field": {
                "file_label": FileLabel.PRIORITY,
                "file": {
                    # "mode": None,
                    # "mode": {
                        # "mode_code": 0xfa,
                        # "special_specifier": 0xbc,
                    # },
                    "message": b"heysexy",
                },
            },
        }

    ],

})))