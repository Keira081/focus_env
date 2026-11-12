"""
Loads and validates rules.yaml.
"""

import yaml
import datetime
from pydantic import BaseModel, model_validator
from typing import Literal, get_args
from pathlib import Path
from rich import print

class Window(BaseModel):
    day_group: str
    start: datetime.time
    end: datetime.time

class LimitEntry(BaseModel):
    day_group: str
    minutes: int

DayName = Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
class Config(BaseModel):
    site_groups: dict[str, list[str]]
    day_groups: dict[str, list[DayName]]
    schedules: dict[str, list[Window]]
    viewing_limits: dict[str, list[LimitEntry]]
    rules: list[dict]

    @model_validator(mode="after") #
    def check_references(self):
        # No missspelled in te schedule object
        for schedule_name, windows in self.schedules.items():
            for window in windows:
                if window.day_group not in self.day_groups:
                    raise ValueError(
                        f"schedules.{schedule_name}: unknown day_group "
                        f"'{window.day_group}'. Known groups: {list(self.day_groups)}"
                    )
        # No missspelled in te viewing_limits object
        for group_name, limit_entries in self.viewing_limits.items():
            for limit_entry in limit_entries:
                if limit_entry.day_group not in self.day_groups:
                   raise ValueError(
                        f"viewing_limits.{group_name}: unknown day_group "
                        f"'{limit_entry.day_group}'. Known groups: {list(self.day_groups)}\n"
                    ) 
        # No repeated days
        group_of_day = {}
        for group_name, days in self.day_groups.items():
            for day in days:
                if day not in group_of_day:
                    group_of_day[day] = group_name
                elif group_of_day[day] == group_name:
                    raise ValueError(
                        f"{day} appears in {group_name} more than once\n"
                    )
                else:
                    raise ValueError(
                        f"{day} appears in {group_of_day[day]} and {group_name}\n"
                    )
        # ensures all days are in a group
        if len(group_of_day) < 7:
            missing = set(get_args(DayName)) - set(group_of_day)
            raise ValueError(
                f"{''.join(sorted(missing))} needs to be added to a group\n"
            )
       
        return self

CONFIG_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"
with open(CONFIG_PATH) as file:
    raw_data = yaml.safe_load(file)

config = Config.model_validate(raw_data)
#print(config)
#print(config.model_dump_json(indent=1))


"""
Learned:
pydantic -> BaseModel: blueprint for what models should look like
^ validates any data that arrives as dicts and lists
pydantic -> <varibleName>.model_validate(data)


path from pathliib: Path(__file__).parent(x how many levels/folders you want to go up by) <path>

Literal from the typing library: defines a fixed set of allowed values
"""