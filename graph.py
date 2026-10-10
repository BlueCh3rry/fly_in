"""Graph representation for the drone simulation (core domain only)."""

import enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

from colors import COLORS


class ZoneType(str, enum.Enum):
    """Enum representing different zone types in the network graph."""

    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class DroneState(str, enum.Enum):
    """Enum representing the current state of a drone."""

    READY = "ready"
    MOVING = "moving"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


@dataclass
class Drone:
    """Represents a drone in the simulation."""

    drone_id: str
    current_zone: str
    state: DroneState = DroneState.READY
    target_zone: str | None = None
    turns_waited: int = 0


class Zone:
    """Represents a zone (vertex) in the network graph."""

    __slots__ = ("name", "x", "y", "zone_type", "color",
                 "max_drones", "priority_bonus")

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str | ZoneType = ZoneType.NORMAL,
        color: str = "white",
        max_drones: int = 1,
        *,
        priority_bonus: float = 0.0,
    ) -> None:
        """Initialize a Zone instance (validates type, color, capacity)."""
        if max_drones <= 0:
            raise ValueError("max_drones must be positive")
        if color is not None and color.lower() not in COLORS:
            raise ValueError(f"Unknown color: {color}")
        try:
            zone_type = ZoneType(zone_type)
        except ValueError:
            raise ValueError(f"Invalid zone type: {zone_type}") from None

        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneType = zone_type
        self.color: str = color
        self.max_drones: int = max_drones
        self.priority_bonus: float = priority_bonus

    def get_cost(self) -> float:
        """Return the movement cost for entering this zone."""
        if self.zone_type is ZoneType.BLOCKED:
            return 100000.0

        base_cost = 2.0 if self.zone_type is ZoneType.RESTRICTED else 1.0
        return base_cost - self.priority_bonus

    def is_blocked(self) -> bool:
        """Return `True` if this zone is blocked."""
        return self.zone_type is ZoneType.BLOCKED


class Connection:
    """Undirected connection (edge) between two zones."""

    __slots__ = ("zone1", "zone2", "max_link_capacity")

    def __init__(
        self, zone1: str, zone2: str, max_link_capacity: int = 1
    ) -> None:
        """Initialize a connection between two zones."""
        if max_link_capacity <= 0:
            raise ValueError("max_link_capacity must be positive")
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity

    def get_zones(self) -> Tuple[str, str]:
        """Return the pair of zone names this connection links."""
        return (self.zone1, self.zone2)


class Graph:
    """Graph of zones and connections using an adjacency list."""

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}
        self.adjacency: Dict[str, List[str]] = {}
        self.start_hub: Zone | None = None
        self.end_hub: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        """Insert *zone* into graph."""
        if zone.name in self.zones:
            raise ValueError(f"Zone '{zone.name}' already exists")
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Insert an undirected connection into the graph."""
        z1, z2 = connection.zone1, connection.zone2
        if z1 not in self.zones or z2 not in self.zones:
            raise ValueError(
                "Both zones must exist in graph before adding a connection"
            )
        if (z1, z2) in self.connections or (z2, z1) in self.connections:
            raise ValueError(f"Connection '{z1}-{z2}' already exists")

        self.connections[(z1, z2)] = connection
        self.connections[(z2, z1)] = connection
        self.adjacency[z1].append(z2)
        self.adjacency[z2].append(z1)

    def get_neighbors(self, zone_name: str) -> List[str]:
        """Return neighbor zone names of *zone_name*."""
        return self.adjacency.get(zone_name, [])

    def get_zone(self, name: str) -> Zone | None:
        """Return the Zone with *name*, or None if absent."""
        return self.zones.get(name)

    def get_connection(self, zone1: str, zone2: str) -> Connection | None:
        """Return the connection between zone1 and zone2, or None."""
        return self.connections.get((zone1, zone2))

    def get_all_zones(self) -> List[Zone]:
        """Return all zones in the graph."""
        return list(self.zones.values())
