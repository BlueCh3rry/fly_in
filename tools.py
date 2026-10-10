from colorama import Fore, Style, init
from typing import Optional
from pydantic import BaseModel, model_validator
from typing import Optional

init(autoreset=True)

RESET = "\033[0m"


def _c256(n: int) -> str:
    """ANSI 256-color foreground code."""
    return f"\033[38;5;{n}m"


COLORS: dict[str, str] = {
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
    "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
    "cyan": "\033[36m", "white": "\033[37m",
    # bright variants
    "gray": "\033[90m", "lightred": "\033[91m", "lightgreen": "\033[92m",
    "lightyellow": "\033[93m", "lightblue": "\033[94m",
    "lightmagenta": "\033[95m", "lightcyan": "\033[96m",
    "lightwhite": "\033[97m",
    # extra
    "orange": _c256(208), "purple": _c256(93), "pink": _c256(213),
    "brown": _c256(94), "gold": _c256(220), "lime": _c256(118),
    "teal": _c256(30), "maroon": _c256(88), "navy": _c256(18),
    "olive": _c256(100), "violet": _c256(129), "crimson": _c256(161),
    "turquoise": _c256(45), "salmon": _c256(209), "beige": _c256(223),
    "silver": _c256(250), "coral": _c256(203), "indigo": _c256(54),
    "rainbow": _c256(196),
}


def get_color(name: str) -> str:
    """Return the ANSI code for a color name (case-insensitive)."""
    return COLORS[name.lower()]


def colorize(text: str, color: str) -> str:
    """Wrap text in the given color."""
    return f"{get_color(color)}{text}{RESET}"


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
        if self.color.lower() not in COLORS:
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
                      colorize(zone.name, zone.color),
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
                  colorize(zone.name, zone.color),
                  f"\tcoord = {zone.coord}",
                  "\tcolor =",
                  colorize(zone.color, zone.color),
                  f"\tstatus = {zone.status}",
                  f"\tlinks = {zone.links}",
                  f"\tmax_drones = {zone.max_drones}")
