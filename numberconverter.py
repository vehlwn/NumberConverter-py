import fractions
import enum
import math


_DIGITS = "0123456789abcdefghijklmnopqrtuvwxyz"


def _getValidDigits(base: int) -> str:
    return _DIGITS[:base]


class _IntFractParts:
    def __init__(self, int_part: str = "", fract_part: str = ""):
        self.int_part = int_part
        self.fract_part = fract_part


def _parse_int_fract_part(s: str, base1: int) -> _IntFractParts:
    def matches(c: str):
        d = _DIGITS.find(c)
        return d != -1 and d < base1

    class State(enum.IntEnum):
        EXPECT_SPACE_OR_DOT_OR_INT_PART_BEGIN = enum.auto()
        EXPECT_INT_PART_MIDDLE_OR_DOT = enum.auto()
        EXPECT_FRACT_PART_BEGIN = enum.auto()
        EXPECT_FRACT_PART_MIDDLE = enum.auto()

    ret = _IntFractParts()

    state = State.EXPECT_SPACE_OR_DOT_OR_INT_PART_BEGIN
    for (i, c) in enumerate(s):
        if state == State.EXPECT_SPACE_OR_DOT_OR_INT_PART_BEGIN:
            if c.isspace():
                continue
            elif matches(c):
                ret.int_part = c
                state = State.EXPECT_INT_PART_MIDDLE_OR_DOT
            elif c == NumberConverter.decimal_point():
                ret.int_part = ""
                state = State.EXPECT_FRACT_PART_BEGIN
            else:
                raise ParserException(
                    f"Invalid character in integer part: '{c}'."
                    f" Expecting space or decimal separator '{NumberConverter.decimal_point()}'"
                    f" or one of valid digits: '{_getValidDigits(base1)}'.",
                    i,
                )

        elif state == State.EXPECT_INT_PART_MIDDLE_OR_DOT:
            if matches(c):
                ret.int_part += c
                continue
            elif c == NumberConverter.decimal_point():
                state = State.EXPECT_FRACT_PART_BEGIN
            else:
                raise ParserException(
                    f"Invalid character in integer part: '{c}'."
                    f" Expecting decimal separator '{NumberConverter.decimal_point()}'"
                    f" or one of valid digits: '{_getValidDigits(base1)}'.",
                    i,
                )

        elif state == State.EXPECT_FRACT_PART_BEGIN:
            if matches(c):
                ret.fract_part = c
                state = State.EXPECT_FRACT_PART_MIDDLE
            else:
                raise ParserException(
                    f"Invalid character in fractional part: '{c}'."
                    f" Expecting one of valid digits: '{_getValidDigits(base1)}'.",
                    i,
                )

        elif state == State.EXPECT_FRACT_PART_MIDDLE:
            if matches(c):
                ret.fract_part += c
            else:
                raise ParserException(
                    f"Invalid character in fractional part: '{c}'."
                    f" Expecting one of valid digits: '{_getValidDigits(base1)}'.",
                    i,
                )

    return ret


def _to_string_base2(num: int, base2: int) -> str:
    ret = ""
    if not num:
        return "0"
    while num:
        (q, r) = divmod(num, base2)
        ret += _DIGITS[r]
        num = q

    ret = ret[::-1]
    return ret


def _to_integer_base1(input_number: str, base1: int) -> int:
    ret = 0
    for c in input_number:
        d = _DIGITS.find(c)
        ret = ret * base1 + d
    return ret


def _fraction_part_to_string(
    num: fractions.Fraction, base2: int, digits_after_point: int
) -> str:
    res = ""

    def fract(num: fractions.Fraction) -> fractions.Fraction:
        return num - math.floor(num)

    for i in range(digits_after_point):
        num = fract(num) * base2
        if not num:
            break
        j = math.floor(num)
        res += _DIGITS[j]
    return res


class ParserException(RuntimeError):
    def __init__(self, msg: str, pos: int):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos


class NumberConverter:
    def __call__(
        self,
        input_number: str = "0",
        base1: int = 10,
        base2: int = 2,
        digits_after_point: int = 20,
    ) -> str:
        self._base1 = base1
        self._base2 = base2
        self._digits_after_point = digits_after_point

        if (
            min(self._base1, self._base2) < self.min_base()
            or max(self._base1, self._base2) > self.max_base()
        ):
            raise RuntimeError(
                f"Base of a number system must be from {self.min_base()} to {self.max_base()}."
            )

        parsed = _parse_int_fract_part(input_number, self._base1)

        int_part = _to_integer_base1(parsed.int_part, self._base1)
        fract_part = fractions.Fraction(
            _to_integer_base1(parsed.fract_part, self._base1),
            pow(self._base1, len(parsed.fract_part)),
        )

        s = _to_string_base2(int_part, self._base2)
        if fract_part and self._digits_after_point > 0:
            s2 = _fraction_part_to_string(
                fract_part, self._base2, self._digits_after_point
            )
            s += NumberConverter.decimal_point() + s2

        return s

    def min_base(self) -> int:
        return 2

    def max_base(self) -> int:
        return len(_DIGITS)

    @staticmethod
    def decimal_point() -> str:
        return "."
