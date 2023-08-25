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
    args = parser.parse_args()
    about_me_path: Path = args.about_me

    about_me = load_about_me(about_me_path)

    print(about_me)


def load_about_me(path: Path) -> AboutMe:
    about_me_dict = yaml.load(path.read_text(), Loader=yaml.FullLoader)
    about_me = AboutMe.model_validate(about_me_dict)
    return about_me


if __name__ == "__main__":
    main()
