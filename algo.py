"""Capacity-aware A* scheduling of drones (reservation-table approach).

Drones are planned one after the other on a time-expanded graph. Each
drone takes the earliest-arrival route that respects what the previous
drones reserved (zone capacity, link capacity, waiting). Ties on arrival
turn are broken in favour of routes through more priority zones.
"""

from __future__ import annotations

import heapq
import itertools
from collections import defaultdict

from graph import Graph

State = tuple[str, int]
LinkKey = tuple[tuple[str, str], int]


class PathNotFoundError(Exception):
    """Raised when the map has no valid route from start to end."""


class ReservationTable:
    """Tracks zone and connection usage per turn."""

    def __init__(self, graph: Graph) -> None:
        """Initialize an empty reservation table.

        Args:
            graph: The graph providing zone and link capacities.
        """
        assert graph.start_hub is not None
        assert graph.end_hub is not None
        self.graph = graph
        self.zone_use: dict[State, int] = defaultdict(int)
        self.link_use: dict[LinkKey, int] = defaultdict(int)
        # Start and end ignore max_drones (see subject, parser rules).
        self._unlimited: set[str] = {
            graph.start_hub.name,
            graph.end_hub.name,
        }

    @staticmethod
    def _connection_key(zone1: str, zone2: str) -> tuple[str, str]:
        """Return a normalized key so a-b and b-a share one counter."""
        z1, z2 = sorted((zone1, zone2))
        return (z1, z2)

    @staticmethod
    def link_turns(depart: int, arrive: int) -> range:
        """Turns during which a move occupies its connection.

        A normal move uses the link on turn depart+1. A restricted move
        also uses it only on depart+1: the link is freed on the arrival
        turn, as the subject requires.
        """
        return range(depart + 1, max(depart + 2, arrive))

    def is_safe(self, zone_name: str, time: int) -> bool:
        """Tell whether a zone can take one more drone at ``time``."""
        if zone_name in self._unlimited:
            return True
        zone = self.graph.get_zone(zone_name)
        assert zone is not None
        return self.zone_use.get((zone_name, time), 0) < zone.max_drones

    def is_connection_safe(self, zone1: str, zone2: str, time: int) -> bool:
        """Tell whether a connection can take one more drone at ``time``."""
        conn = self.graph.get_connection(zone1, zone2)
        assert conn is not None
        key = (self._connection_key(zone1, zone2), time)
        return self.link_use.get(key, 0) < conn.max_link_capacity

    def is_move_safe(
        self, zone1: str, zone2: str, depart: int, arrive: int
    ) -> bool:
        """Check link capacity during the crossing and zone at arrival."""
        links_ok = all(
            self.is_connection_safe(zone1, zone2, t)
            for t in self.link_turns(depart, arrive)
        )
        return links_ok and self.is_safe(zone2, arrive)

    def reserve_path(self, path: list[State]) -> None:
        """Reserve every zone-time and connection-time used by a path.

        Args:
            path: List of (zone_name, time) tuples, waits included.
        """
        for (from_zone, from_time), (to_zone, to_time) in zip(
            path, path[1:]
        ):
            if from_zone != to_zone:
                key = self._connection_key(from_zone, to_zone)
                for t in self.link_turns(from_time, to_time):
                    self.link_use[(key, t)] += 1
            self.zone_use[(to_zone, to_time)] += 1

    def print_link_usage(self) -> None: # added here
        print("\n=== CONNECTION USAGE ===")
        for (connection, turn), count in sorted(
            self.link_use.items(),
            key=lambda item: (item[0][1], item[0][0]),
        ):
            print(
                f"Turn {turn} | {connection[0]}-{connection[1]} "
                f"| Drones: {count}"
            )

class Node:
    """Represents a node in the A* search tree."""

    def __init__(
        self,
        name: str,
        time: int,
        penalty: int,
        h: int,
        parent: Node | None,
    ) -> None:
        """Initialize a search node.

        Args:
            name: The zone name.
            time: Turn at which the drone is in this zone.
            penalty: Non-priority zones entered so far (lower is better).
            h: Heuristic turns left to the end zone.
            parent: The parent node in the search tree.
        """
        self.name = name
        self.time = time
        self.penalty = penalty
        self.heuristic_to_end = h
        self.estimated_total_cost = time + h
        self.parent = parent


class Pathfinder:
    """A* scheduling of all drones with conflict avoidance."""

    def __init__(self, graph: Graph, nb_drones: int) -> None:
        """Initialize pathfinder.

        Args:
            graph: The graph structure containing zones and connections.
            nb_drones: The number of drones to route.
        """
        self.graph = graph
        self.drone_ids = [f"D{i}" for i in range(1, nb_drones + 1)]
        self.heuristics = self._compute_heuristics()

    def _turns(self, name: str) -> int | None:
        """Turns needed to enter a zone, None if it is blocked."""
        zone = self.graph.get_zone(name)
        assert zone is not None
        if zone.is_blocked():
            return None
        return 2 if zone.zone_type == "restricted" else 1

    def _is_priority(self, name: str) -> bool:
        """Tell whether a zone is a priority zone."""
        zone = self.graph.get_zone(name)
        assert zone is not None
        return zone.zone_type == "priority"

    def _compute_heuristics(self) -> dict[str, int]:
        """Minimum turns from every zone to the end hub.

        Reverse Dijkstra: entering a zone costs its own turn cost, so
        restricted zones count double. Blocked and unreachable zones are
        absent from the result.

        Returns:
            Dictionary mapping zone names to their turns-to-end.
        """
        assert self.graph.end_hub is not None
        end = self.graph.end_hub.name
        dist: dict[str, int] = {end: 0}
        heap: list[tuple[int, str]] = [(0, end)]

        while heap:
            d, current = heapq.heappop(heap)
            if d > dist[current]:
                continue
            step = self._turns(current)  # cost paid to enter `current`
            if step is None:
                continue
            for neighbor in self.graph.get_neighbors(current):
                if self._turns(neighbor) is None:
                    continue
                nd = d + step
                if nd < dist.get(neighbor, nd + 1):
                    dist[neighbor] = nd
                    heapq.heappush(heap, (nd, neighbor))
        return dist

    def schedule_moves(
        self, max_time: int | None = None
    ) -> dict[int, dict[str, str]]:
        """Schedule moves for all drones to minimize total turns.

        Args:
            max_time: Time horizon. Default: safe upper bound computed
                from the shortest path and the number of drones.

        Returns:
            Dict turn -> {drone id: destination zone, or "from-to"
            connection name while a drone is in flight}.

        Raises:
            PathNotFoundError: If the end is unreachable.
        """
        assert self.graph.start_hub is not None
        start = self.graph.start_hub.name
        if start not in self.heuristics:
            raise PathNotFoundError(
                "No path connects the start hub to the end hub")

        if max_time is None:
            # Worst case: drones cross strictly one after another.
            max_time = self.heuristics[start] * (len(self.drone_ids) + 1) + 2

        table = ReservationTable(self.graph)
        moves_by_turn: dict[int, dict[str, str]] = defaultdict(dict)

        for d_id in self.drone_ids:
            path = self._astar(table, max_time)
            if path is None:
                raise PathNotFoundError(
                    f"No schedule found for {d_id} within {max_time} turns")
            table.reserve_path(path)
            self._add_moves(moves_by_turn, d_id, path)
        table.print_link_usage() # added here
        return dict(moves_by_turn)

    def _successors(
        self, current: Node, table: ReservationTable
    ) -> list[tuple[str, int, int]]:
        """Legal moves from a node: (zone, arrival time, penalty added)."""
        result: list[tuple[str, int, int]] = []

        if table.is_safe(current.name, current.time + 1):
            result.append((current.name, current.time + 1, 0))

        for neighbor in self.graph.get_neighbors(current.name):
            turns = self._turns(neighbor)
            if turns is None:
                continue
            arrive = current.time + turns
            if table.is_move_safe(
                    current.name, neighbor, current.time, arrive):
                extra = 0 if self._is_priority(neighbor) else 1
                result.append((neighbor, arrive, extra))
        return result

    def _astar(
        self, table: ReservationTable, max_depth: int
    ) -> list[State] | None:
        """A* from start to end over (zone, time) states.

        States are ordered by (time + heuristic, non-priority count), so
        arrival time always wins and priority zones only break ties.

        Args:
            table: Reservation table for conflict checking.
            max_depth: Maximum turn (time horizon).

        Returns:
            List of (zone_name, time) tuples, or None if no path found.
        """
        assert self.graph.start_hub is not None
        assert self.graph.end_hub is not None
        start = self.graph.start_hub.name
        end = self.graph.end_hub.name

        counter = itertools.count()
        root = Node(start, 0, 0, self.heuristics[start], None)
        open_set: list[tuple[int, int, int, Node]] = [
            (root.estimated_total_cost, 0, next(counter), root)
        ]
        closed: set[State] = set()

        while open_set:
            _, _, _, current = heapq.heappop(open_set)
            key = (current.name, current.time)
            if key in closed:
                continue
            closed.add(key)

            if current.name == end:
                return self._rebuild(current)
            if current.time >= max_depth:
                continue

            for name, arrive, extra in self._successors(current, table):
                h = self.heuristics.get(name)
                if h is None:
                    continue
                node = Node(name, arrive, current.penalty + extra, h,
                            current)
                heapq.heappush(
                    open_set,
                    (node.estimated_total_cost, node.penalty,
                     next(counter), node),
                )
        return None

    @staticmethod
    def _rebuild(node: Node) -> list[State]:
        """Follow parents back to the root and return the path."""
        path: list[State] = []
        current: Node | None = node
        while current is not None:
            path.append((current.name, current.time))
            current = current.parent
        path.reverse()
        return path

    @staticmethod
    def _add_moves(
        moves_by_turn: dict[int, dict[str, str]],
        d_id: str,
        path: list[State],
    ) -> None:
        """Convert a path into per-turn output tokens.

        A 1-turn move gives the zone name on the arrival turn. A
        restricted move gives the connection name while in flight, then
        the zone name on arrival.
        """
        for (from_zone, from_time), (to_zone, to_time) in zip(
            path, path[1:]
        ):
            if from_zone == to_zone:
                continue  # waiting: nothing printed
            for turn in range(from_time + 1, to_time):
                moves_by_turn[turn][d_id] = f"{from_zone}-{to_zone}"
            moves_by_turn[to_time][d_id] = to_zone

    @staticmethod
    def format_output(moves_by_turn: dict[int, dict[str, str]]) -> list[str]:
        """Build the simulation output: one line per turn."""
        if not moves_by_turn:
            return []
        lines: list[str] = []
        for turn in range(1, max(moves_by_turn) + 1):
            moves = moves_by_turn.get(turn, {})
            ordered = sorted(moves.items(), key=lambda m: int(m[0][1:]))
            lines.append(" ".join(f"{d}-{dest}" for d, dest in ordered))
        return lines
