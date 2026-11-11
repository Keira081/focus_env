"""
Loads and validates rules.yaml.
"""

import yaml
import datetime
from pydantic import BaseModel
from typing import Literal
from pathlib import Path
from rich import print

class Window(BaseModel):
    day_group: str
    start: datetime.time
    end: datetime.time

class LimitEntry(BaseModel):
    day_group: str
    minutes: int

dayName = Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
class Config(BaseModel):
    site_groups: dict[str, list[str]]
    day_groups: dict[str, list[dayName]]
    schedules: dict[str, list[Window]]
    viewing_limits: dict[str, list[LimitEntry]]
    rules: list[dict]

CONFIG_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"
with open(CONFIG_PATH) as file:
    raw_data = yaml.safe_load(file)

config = Config.model_validate(raw_data)
print(config)
#print(config.model_dump_json(indent=1))


