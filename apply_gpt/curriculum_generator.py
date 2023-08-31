from typing import Protocol

from apply_gpt.data import AboutMe, Curriculum, Month
from apply_gpt.openai_ import OpenaiJsonGenerator
from apply_gpt.text_converter import TextConverter


class CurriculumGenerator(Protocol):
    def generate_curriculum(
        self, about_me: AboutMe, job_description: str
    ) -> Curriculum:
        ...


class OpenaiCurriculumGenerator(CurriculumGenerator):
    EMPLOYMENTS_TOKEN = "{{EMPLOYMENTS}}"
    EDUCATIONS_TOKEN = "{{EDUCATIONS}}"
    JOB_DESCRIPTION_TOKEN = "{{JOB_DESCRIPTION}}"

    def __init__(
        self,
        text_converter: TextConverter,
        openai_json_generator: OpenaiJsonGenerator,
        system_message: str,
        user_message_template: str,
    ) -> None:
        self._text_converter = text_converter
        self._openai_json_generator = openai_json_generator
        self._system_message = system_message

        employments_token_count = user_message_template.count(
            OpenaiCurriculumGenerator.EMPLOYMENTS_TOKEN
        )
        educations_token_count = user_message_template.count(
            OpenaiCurriculumGenerator.EDUCATIONS_TOKEN
        )
        job_description_token_count = user_message_template.count(
            OpenaiCurriculumGenerator.JOB_DESCRIPTION_TOKEN
        )
        if (
            employments_token_count != 1
            or educations_token_count != 1
            or job_description_token_count != 1
        ):
            raise ValueError(
                "All tokens should appear exactly once in user message template, "
                f"{OpenaiCurriculumGenerator.EMPLOYMENTS_TOKEN} "
                f"found {employments_token_count} times, "
                f"{OpenaiCurriculumGenerator.EDUCATIONS_TOKEN} "
                f"found {educations_token_count} times, "
                f"{OpenaiCurriculumGenerator.JOB_DESCRIPTION_TOKEN} "
                f"found {job_description_token_count} times"
            )
        self._user_message_template = user_message_template

    def generate_curriculum(
        self, about_me: AboutMe, job_description: str
    ) -> Curriculum:
        employments = "\n".join(
            self._text_converter.textify_employment(e) for e in about_me.employments
        )
        educations = "\n".join(
            self._text_converter.textify_education(e) for e in about_me.educations
        )
        user_message = (
            self._user_message_template.replace(
                OpenaiCurriculumGenerator.EMPLOYMENTS_TOKEN, employments
            )
            .replace(OpenaiCurriculumGenerator.EDUCATIONS_TOKEN, educations)
            .replace(OpenaiCurriculumGenerator.JOB_DESCRIPTION_TOKEN, job_description)
        )

        curriculum_json = self._openai_json_generator.generate(
            system_message=self._system_message,
            user_message=user_message,
            name=OpenaiCurriculumGenerator._CURRICULUM_NAME,
            schema=OpenaiCurriculumGenerator._CURRICULUM_SCHEMA,
        )

        curriculum = Curriculum.model_validate(curriculum_json)

        return curriculum

    _CURRICULUM_NAME = "curriculum"

    # NOTE: Possible solutions to move this to file for easier prompt engineering
    # 1) Move to file only the descriptions of the fields
    # 2) Extract to a file the way to map Curriculum schema to Curriculum object
    _CURRICULUM_SCHEMA: OpenaiJsonGenerator.Schema = {
        "type": "object",
        "required": ("employments", "educations", "skillsets"),
        "description": "The curriculum to generate",
        "properties": {
            "employments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": (
                        "role",
                        "company",
                        "start_date",
                        "achievements",
                    ),
                    "properties": {
                        "role": {"type": "string"},
                        "company": {"type": "string"},
                        "start_date": {
                            "type": "object",
                            "required": ("year",),
                            "properties": {
                                "year": {"type": "number"},
                                "month": {
                                    "type": "string",
                                    "enum": [m.value for m in Month],
                                },
                            },
                        },
                        "end_date": {
                            "type": "object",
                            "required": ("year",),
                            "properties": {
                                "year": {"type": "number"},
                                "month": {
                                    "type": "string",
                                    "enum": [m.value for m in Month],
                                },
                            },
                        },
                        "achievements": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "educations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": (
                        "degree",
                        "institution",
                        "start_date",
                        "achievements",
                    ),
                    "properties": {
                        "degree": {"type": "string"},
                        "institution": {"type": "string"},
                        "grade": {"type": "string"},
                        "start_date": {
                            "type": "object",
                            "required": ("year",),
                            "properties": {
                                "year": {"type": "number"},
                                "month": {
                                    "type": "string",
                                    "enum": [m.value for m in Month],
                                },
                            },
                        },
                        "end_date": {
                            "type": "object",
                            "required": ("year",),
                            "properties": {
                                "year": {"type": "number"},
                                "month": {
                                    "type": "string",
                                    "enum": [m.value for m in Month],
                                },
                            },
                        },
                        "achievements": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "skillsets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ("name", "skills"),
                    "properties": {
                        "name": {"type": "string"},
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
        },
    }
