import json
import random
from typing import Protocol, Sequence

from apply_gpt.openai_ import OpenaiManualJsonGenerator


class AchievementsTuner(Protocol):
    def tune_achievements(
        self,
        achievements: Sequence[str],
        job_description: str,
        max_achievements: int | None = None,
    ) -> Sequence[str]:
        ...


class OpenaiManualAchievementsTuner(AchievementsTuner):
    def __init__(
        self,
        openai_manual_json_generator: OpenaiManualJsonGenerator,
        job_skills_msg_prefix: str,
        achievements_skills_msg_prefix: str,
        achievements_sort_msg_prefix: str,
        achievements_reword_msg_prefix: str,
    ) -> None:
        self._openai_manual_json_generator = openai_manual_json_generator
        self._job_skills_msg_prefix = job_skills_msg_prefix
        self._achievements_skills_msg_prefix = achievements_skills_msg_prefix
        self._achievements_sort_msg_prefix = achievements_sort_msg_prefix
        self._achievements_reword_msg_prefix = achievements_reword_msg_prefix

    def tune_achievements(
        self,
        achievements: Sequence[str],
        job_description: str,
        max_achievements: int | None = None,
    ) -> Sequence[str]:
        self._openai_manual_json_generator.generate(
            f"{self._job_skills_msg_prefix}\n" f"{job_description}"
        )

        random.sample(achievements, len(achievements))

        id_to_achievement = {
            f"{id_}": achievement
            for id_, achievement in enumerate(achievements, start=1)
        }

        id_to_achievement_str = json.dumps(id_to_achievement, indent=2)
        id_to_skills: dict[
            str, Sequence[str]
        ] = self._openai_manual_json_generator.generate(  # type: ignore[assignment]
            f"{self._achievements_skills_msg_prefix}\n" f"{id_to_achievement_str}"
        )

        id_to_skills_str = json.dumps(id_to_skills, indent=2)
        sorted_ids: Sequence[
            str
        ] = self._openai_manual_json_generator.generate(  # type: ignore[assignment]
            f"{self._achievements_sort_msg_prefix}\n" f"{id_to_skills_str}"
        )

        if max_achievements is not None:
            selected_ids = sorted_ids[:max_achievements]
        else:
            selected_ids = sorted_ids

        selected_achievements = [id_to_achievement[id_] for id_ in selected_ids]
        selected_achievements_str = json.dumps(selected_achievements, indent=2)

        tuned_achievements: Sequence[
            str
        ] = self._openai_manual_json_generator.generate(  # type: ignore[assignment]
            f"{self._achievements_reword_msg_prefix}\n" f"{selected_achievements_str}"
        )

        return tuned_achievements
