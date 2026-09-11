from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ValidationError, model_validator


MAX_DRONES_SIZE = 400


class colors(str, Enum):
    none = ""
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


class Drone(BaseModel):
    id: int
    location: list[int]


class Zone(BaseModel):
    name: str
    coord: tuple[int, int]
    color: colors
    status: Optional[str]
    links: Optional[tuple[tuple[str, str], ...]]
    max_drones: Optional[int] = Field(ge=1, le=MAX_DRONES_SIZE)

    @model_validator(mode="after")
    def validate_zone_rules(self):
        if self.status not in ("restricted", "normal", "blocked", "priority"):
            raise ValidationError("status is not correct")
        elif self.status is None:
            self.status = "normal"
        if self.status is None:
            self.max_drones = 1


class Zone_queue(BaseModel):
    drones_waiting_nbr: int
    drones_lst: list[Drone]
    max_link_capacity: int
    zone_location: tuple[str, str]


class Data(BaseModel):
    drones: int
    start: Zone
    end: Zone
    zones: tuple[Zone, ...]
    lst_drones: tuple[Drone, ...]
    zone_queues: tuple[Zone_queue, ...]

    @model_validator(mode="after")
    def validate_rules(self):
        print("testing")

    def show_links(self):
        for zone in self.zones:
            print(f"{zone.links if zone.links is not None else ''}\n")

    def show_queue(self, zone_1: Zone, zone_2: Zone):
        for queue in self.zone_queues:
            if queue.zone_location == (zone_1, zone_2):
                print(f"\tzone location = {queue.zone_location}",
                      f"\t\tdrones lst = {queue.drones_lst}",
                      f"\t\tmax link capacity = {queue.max_link_capacity}",
                      f"\t\tzone location = {queue.zone_location}",
                      f"\t\tdrones waiting nbr = {queue.drones_waiting_nbr}")