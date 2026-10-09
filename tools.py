from colorama import Fore, Style, init
from typing import Optional
from pydantic import BaseModel, model_validator

init(autoreset=True)


class Drone(BaseModel):
    name: str
    id: int
    location: list[int]


class Zone(BaseModel):
    name: str
    coord: tuple[int, int]
    color: str
    status: Optional[str]
    links: Optional[tuple[tuple[str, str], ...]]
    max_drones: int

    @model_validator(mode="after")
    def validate_zone_rules(self):
        if self.status is not None and self.status not in ("restricted",
                                                           "normal",
                                                           "blocked",
                                                           "priority"):
            raise ValueError("status is not correct for Zone(BaseModel)")
        elif self.status is None:
            self.status = "normal"
        if not hasattr(Fore, self.color):
            raise ValueError(
                f"Color is not correct for Zone(BaseModel), got: {self.color}")
        if self.max_drones <= 0:
            raise ValueError("max_drones is not correct for Zone(BaseModel)")
        return self


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
        # print("testing")
        return self

    def show_links(self):
        print("All connections info, 'show_links()':")
        for zone in self.zones:
            print(f"\t{zone.links if zone.links is not None else 'None'}")

    def show_queue(self, zone_1: Zone, zone_2: Zone):
        print("Target queue info, 'show__queue()':")
        for queue in self.zone_queues:
            if queue.zone_location == (zone_1, zone_2):
                print(f"\tzone location = {queue.zone_location}",
                      f"\tdrones lst = {queue.drones_lst}",
                      f"\tmax link capacity = {queue.max_link_capacity}",
                      f"\tzone location = {queue.zone_location}",
                      f"\tdrones waiting nbr = {queue.drones_waiting_nbr}")

    def show_zone(self, zone_1: Zone):
        print("All zones info, 'show_all_zones()':")
        for zone in self.zones:
            if zone.name == zone_1:
                print("\tname =",
                      getattr(Fore, zone.color) + zone.name + Style.RESET_ALL,
                      f"\tcoord = {zone.coord}",
                      f"\tcolor = {zone.color}",
                      f"\tstatus = {zone.status}",
                      f"\tlinks = {zone.links}",
                      f"\tmax_drones = {zone.max_drones}")

    def show_all_queues(self):
        print("All queues info, 'show_all_queues()':")
        for queue in self.zone_queues:
            print(f"\tzone = {queue.zone_location}:",
                  f"\tdrones lst = {queue.drones_lst}",
                  f"\tmax link capacity = {queue.max_link_capacity}",
                  f"\tdrones waiting nbr = {queue.drones_waiting_nbr}")

    def show_all_zones(self):
        print("All zones info, 'show_all_zones()':")
        for zone in self.zones:
            print("\tname =",
                  getattr(Fore, zone.color) + zone.name + Style.RESET_ALL,
                  f"\tcoord = {zone.coord}",
                  "\tcolor =",
                  getattr(Fore, zone.color) + zone.color + Style.RESET_ALL,
                  f"\tstatus = {zone.status}",
                  f"\tlinks = {zone.links}",
                  f"\tmax_drones = {zone.max_drones}")
