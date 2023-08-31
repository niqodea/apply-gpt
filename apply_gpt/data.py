import re
from enum import Enum
from typing import Any, ClassVar, Pattern, Sequence

from pydantic import BaseModel, NonNegativeInt, root_validator, validator


class Private(BaseModel):
    name: str
    address: str | None
    phone: str | None  # TODO maybe switch to PhoneNumber
    mail: str  # TODO maybe switch to EmailStr
    linkedin: str | None
    github: str | None


class Month(Enum):
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"


class Date(BaseModel):
    year: NonNegativeInt

    _DATE_REGEX: ClassVar[Pattern[str]] = re.compile(r"(\d+)")

    @root_validator(pre=True)
    def parse_str(cls, root: Any) -> dict:
        if not isinstance(root, str):
            return root

        sanitized_string = root.strip()

        re_match = Date._DATE_REGEX.match(sanitized_string)
        if re_match is None:
            raise ValueError(f"Could not parse string `{root}`")

        year = re_match.group(1)
        return dict(year=year)


class DetailedDate(Date):
    month: Month

    _DETAILED_DATE_REGEX: ClassVar[Pattern[str]] = re.compile(
        rf"({'|'.join(m.value for m in Month)}) +(\d+)"
    )

    @root_validator(pre=True)
    def parse_str(cls, root: Any) -> dict:
        if not isinstance(root, str):
            return root

        sanitized_string = root.strip().lower()

        re_match = DetailedDate._DETAILED_DATE_REGEX.match(sanitized_string)
        if re_match is None:
            raise ValueError(f"Could not parse string `{root}`")

        month = re_match.group(1)
        year = re_match.group(2)
        return dict(year=year, month=month)


def is_before(date_a: Date, date_b: Date) -> bool | None:
    if date_a.year < date_b.year:
        return True
    elif date_a.year > date_b.year:
        return False

    if not isinstance(date_a, DetailedDate) or not isinstance(date_b, DetailedDate):
        return None

    end_month_index = list(Month).index(date_a.month)
    start_month_index = list(Month).index(date_b.month)

    if end_month_index < start_month_index:
        return True
    elif end_month_index > start_month_index:
        return False

    return None


class Employment(BaseModel):
    role: str
    company: str
    start_date: DetailedDate | Date
    end_date: DetailedDate | Date | None = None
    achievements: Sequence[str] | None = None

    @validator("end_date")
    def end_after_start(
        cls, end_date: Date | None, values: dict[str, Any]
    ) -> Date | None:
        if end_date is None:
            return end_date

        start_date: Date = values["start_date"]

        if is_before(end_date, start_date) is True:
            raise ValueError(f"End date before start date: {end_date} < {start_date}")

        return end_date


class Education(BaseModel):
    degree: str
    institution: str
    grade: str | None = None
    start_date: DetailedDate | Date
    end_date: DetailedDate | Date | None = None
    achievements: Sequence[str] | None = None

    @validator("end_date")
    def end_after_start(
        cls, end_date: Date | None, values: dict[str, Any]
    ) -> Date | None:
        if end_date is None:
            return end_date

        start_date: Date = values["start_date"]

        if is_before(end_date, start_date) is True:
            raise ValueError(f"End date before start date: {end_date} < {start_date}")

        return end_date


class AboutMe(BaseModel):
    private: Private
    employments: Sequence[Employment]
    educations: Sequence[Education]


class Skillset(BaseModel):
    name: str
    skills: Sequence[str]


class Curriculum(BaseModel):
    employments: Sequence[Employment]
    educations: Sequence[Education]
    skillsets: Sequence[Skillset]
