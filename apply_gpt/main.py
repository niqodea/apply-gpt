import argparse
import json
import os
from pathlib import Path

import yaml

from apply_gpt.curriculum_generator import (
    CurriculumGenerator,
    OpenaiCurriculumGenerator,
)
from apply_gpt.data import AboutMe
from apply_gpt.openai_ import OpenaiJsonGenerator, OpenaiModule
from apply_gpt.text_converter import SimpleTextConverter, TextConverter

_OPENAI_ASSETS_PATH = Path(__file__).parent / "openai-assets"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--about-me",
        type=Path,
        help="Path to the YAML file with information about the user",
    )
    parser.add_argument(
        "-j",
        "--job-description",
        type=Path,
        help="Path to the raw text file containing the job description",
    )
    parser.add_argument(
        "--openai-model",
        type=str,
        default="gpt-4-0613",
        help="The OpenAI model to use (more at https://platform.openai.com/docs/models)",
    )
    parser.add_argument(
        "--openai-system-message",
        type=Path,
        default=_OPENAI_ASSETS_PATH / "system-message.txt",
        help="Path to the text file containing the system message for OpenAI API",
    )
    parser.add_argument(
        "--openai-user-message-template",
        type=Path,
        default=_OPENAI_ASSETS_PATH / "user-message-template.txt",
        help=(
            "Path to the text file containing the user message template for OpenAI API"
        ),
    )

    args = parser.parse_args()
    about_me_path: Path = args.about_me
    job_description_path: Path = args.job_description
    openai_model: str = args.openai_model
    openai_system_message_path: Path = args.openai_system_message
    openai_user_message_template_path: Path = args.openai_user_message_template

    about_me = create_about_me(about_me_path)
    job_description = job_description_path.read_text()
    curriculum_generator: CurriculumGenerator = create_openai_curriculum_generator(
        model=openai_model,
        system_message_path=openai_system_message_path,
        user_message_template_path=openai_user_message_template_path,
    )

    curriculum = curriculum_generator.generate_curriculum(
        about_me=about_me, job_description=job_description
    )

    output_path = (
        f"{openai_model}_{about_me_path.stem}_{job_description_path.stem}.json"
    )
    with open(output_path, "w") as f:
        json.dump(curriculum.model_dump(), f, indent=2)


def create_about_me(path: Path) -> AboutMe:
    about_me_dict = yaml.load(path.read_text(), Loader=yaml.FullLoader)
    about_me = AboutMe.model_validate(about_me_dict)
    return about_me


def create_openai_curriculum_generator(
    model: str, system_message_path: Path, user_message_template_path: Path
) -> OpenaiCurriculumGenerator:
    text_converter: TextConverter = SimpleTextConverter()
    openai_module = OpenaiModule(api_key=os.environ["OPENAI_API_KEY"], model=model)
    openai_json_generator = OpenaiJsonGenerator(openai_module=openai_module)
    system_message = system_message_path.read_text()
    user_message_template = user_message_template_path.read_text()

    openai_curriculum_generator = OpenaiCurriculumGenerator(
        text_converter=text_converter,
        openai_json_generator=openai_json_generator,
        system_message=system_message,
        user_message_template=user_message_template,
    )

    return openai_curriculum_generator


if __name__ == "__main__":
    main()
