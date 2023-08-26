import argparse
from pathlib import Path

import yaml

from apply_gpt.data import AboutMe


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
    args = parser.parse_args()
    about_me_path: Path = args.about_me
    job_description_path: Path = args.job_description

    about_me = load_about_me(about_me_path)
    job_description = job_description_path.read_text()

    print(about_me)
    print(job_description)


def load_about_me(path: Path) -> AboutMe:
    about_me_dict = yaml.load(path.read_text(), Loader=yaml.FullLoader)
    about_me = AboutMe.model_validate(about_me_dict)
    return about_me


if __name__ == "__main__":
    main()
