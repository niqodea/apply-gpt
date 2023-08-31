from typing import Protocol

from apply_gpt.data import Date, DetailedDate, Education, Employment


class TextConverter(Protocol):
    def textify_employment(self, employment: Employment) -> str:
        ...

    def textify_education(self, education: Education) -> str:
        ...


class SimpleTextConverter(TextConverter):
    def textify_employment(self, employment: Employment) -> str:
        text = ""
        text += f"Role: {employment.role}\n"
        text += f"Company: {employment.company}\n"
        text += f"{self._textify_period(employment.start_date, employment.end_date)}\n"
        if employment.achievements is not None:
            text += "List of achievements:\n"
            text += "\n".join(f"- {a}" for a in employment.achievements)
        return text

    def textify_education(self, education: Education) -> str:
        text = ""
        text += f"Degree: {education.degree}\n"
        text += f"Institution: {education.institution}\n"
        if education.grade is not None:
            text += f"Grade: {education.grade}\n"
        text += f"{self._textify_period(education.start_date, education.end_date)}\n"
        if education.achievements is not None:
            text += "List of achievements:\n"
            text += "\n".join(f"- {a}" for a in education.achievements)
        return text

    def _textify_period(self, start_date: Date, end_date: Date | None) -> str:
        text = f"Period: {self._textify_date(start_date)} to "
        if end_date is not None:
            text += f"{self._textify_date(end_date)}"
        else:
            text += "present"
        return text

    def _textify_date(self, date: Date) -> str:
        if isinstance(date, DetailedDate):
            return f"{date.month.value.capitalize()} {date.year}"
        else:
            return f"{date.year}"
