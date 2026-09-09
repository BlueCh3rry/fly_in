from enum import Enum
from typing import Union, Optional
from pydantic import BaseModel, Field, ValidationError, model_validator


MAX_DRONES_SIZE = 400


class colors(str, Enum):
    red = "red"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    brown = "brown"
    black = "black"
    white = "white"
    gray = "gray"


class Zone(BaseModel):
    name: str
    coord: tuple[int, int]
    color: colors
    status: Optional[str]
    links: Optional[tuple[str, ...]]
    max_drones: Optional[int] = Field(ge=1, le=MAX_DRONES_SIZE)

    @model_validator(mode="after")
    def validate_zone_rules(self):
        if self.status not in ("restricted", "normal", "blocked", "priority"):
            raise ValidationError("status is not correct")
        elif self.status is None:
            self.status = "normal"
        if self.status is None:
            self.max_drones = 1


class Data(BaseModel):
    drones: int
    start: Zone
    end: Zone
    zones: list[Zone]

    @model_validator(mode="after")
    def validate_rules(self):
        print("testing")


    def show_links(self):
        for zone in self.zones:
            print(f"{zone.links if zone.links is not None else ''}\n")


def main():
    m1 = Data()
    print(m1)
