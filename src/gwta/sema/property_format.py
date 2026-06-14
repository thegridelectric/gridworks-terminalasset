import re
import uuid
from typing import Annotated

from pydantic import BeforeValidator, Field, StrictFloat


# --- patterns ---
HANDLE_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*$"
)

LEFT_RIGHT_DOT_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)*$")

PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]*$")

SPACEHEAT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

UUID4_STR_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


# --- methods ---
def is_handle_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: HandleName must be a string.")

    if not HANDLE_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails HandleName format.")

    return v


def is_left_right_dot(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: LeftRightDot must be a string.")

    if not LEFT_RIGHT_DOT_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails LeftRightDot format.")

    return v


def is_pascal_case(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: PascalCase must be a string.")

    if not PASCAL_CASE_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails PascalCase format.")

    return v


def is_positive_int(v: int) -> int:
    if not isinstance(v, int) or isinstance(v, bool):
        raise TypeError("Not an int!")
    if v <= 0:
        raise ValueError(f"{v} must be positive")
    return v


def is_spaceheat_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: SpaceheatName must be a string.")

    if len(v) > 64:
        raise ValueError(f"<{v}>: SpaceheatName exceeds maximum length of 64.")

    if not SPACEHEAT_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails SpaceheatName format.")

    return v


def is_uuid4_str(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: uuid4.str must be a string.")

    if not UUID4_STR_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails uuid4.str format.")

    try:
        u = uuid.UUID(v)
    except Exception as e:
        raise ValueError(f"Invalid UUID4: {v}  <{e}>") from e
    if u.version != 4:
        raise ValueError(
            f"{v} is valid uid, but of version {u.version}. Fails UuidCanonicalTextual"
        )
    return str(u)


# --- annotated types ---
HandleName = Annotated[
    str,
    BeforeValidator(is_handle_name),
]

LeftRightDot = Annotated[
    str,
    BeforeValidator(is_left_right_dot),
]

NonEmptyString = Annotated[
    str,
    Field(min_length=1),
]

PascalCase = Annotated[
    str,
    BeforeValidator(is_pascal_case),
]

PositiveFloat = Annotated[
    StrictFloat,
    Field(gt=0),
]

PositiveInt = Annotated[
    int,
    BeforeValidator(is_positive_int),
]

SpaceheatName = Annotated[
    str,
    BeforeValidator(is_spaceheat_name),
]

UUID4Str = Annotated[
    str,
    BeforeValidator(is_uuid4_str),
]
