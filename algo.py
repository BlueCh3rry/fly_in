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


class PathNotFoundError(Exception):
    """Raised when the map has no valid route from start to end."""


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
        assert graph.start_hub is not None and graph.end_hub is not None
        graph.start_hub.unlimited = True
        graph.end_hub.unlimited = True
        self.heuristics = self.compute_heuristics()

    @staticmethod
    def link_turns(depart: int, arrive: int) -> range:
        """Turns a move occupies its link (depart+1 only)."""
        return range(depart + 1, max(depart + 2, arrive))

    def is_move_safe(
        self, src: str, dst: str, depart: int, arrive: int
    ) -> bool:
        """Link free during crossing and destination free on arrival."""
        conn = self.graph.get_connection(src, dst)
        zone = self.graph.get_zone(dst)
        assert conn is not None and zone is not None
        if zone.is_full(arrive):
            return False
        return not any(
            conn.is_full(t) for t in self.link_turns(depart, arrive)
        )

    def reserve_path(self, path: list[State]) -> None:
        """Mark every zone-time and link-time used by a path as occupied."""
        for (a, t0), (b, t1) in zip(path, path[1:]):
            if a != b:
                conn = self.graph.get_connection(a, b)
                assert conn is not None
                for t in self.link_turns(t0, t1):
                    conn.occupy(t)
            zone = self.graph.get_zone(b)
            assert zone is not None
            zone.occupy(t1)

    def print_usage_by_turn(self) -> None:
        """Shows current occupied size in zones and connections"""
        zones = self.graph.zones.values()
        conns = {id(c): c for c in self.graph.connections.values()}.values()
        turns = sorted(
            {t for z in zones for t in z.occupied}
            | {t for c in conns for t in c.occupied}
        )
        for turn in turns:
            print(f"\nTurn {turn}:")
            for zone in sorted(zones, key=lambda z: z.name):
                cont = zone.occupied.get(turn, 0)
                if cont:
                    print(f"zone {zone.name}: {cont}/{zone.max_drones} drones")
            for conn in sorted(conns, key=lambda c: (c.zone1, c.zone2)):
                if conn.occupied.get(turn, 0):
                    print(f"connection {conn.usage(turn)}")

    def turns(self, name: str) -> int | None:
        """Turns needed to enter a zone, None if it is blocked."""
        zone = self.graph.get_zone(name)
        assert zone is not None
        if zone.is_blocked():
            return None
        return 2 if zone.zone_type == "restricted" else 1

    def is_priority(self, name: str) -> bool:
        """Tell whether a zone is a priority zone."""
        zone = self.graph.get_zone(name)
        assert zone is not None
        return zone.zone_type == "priority"

    def compute_heuristics(self) -> dict[str, int]:
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
            step = self.turns(current)  # cost paid to enter `current`
            if step is None:
                continue
            for neighbor in self.graph.get_neighbors(current):
                if self.turns(neighbor) is None:
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

        self.graph.reset_occupancy()
        moves_by_turn: dict[int, dict[str, str]] = defaultdict(dict)

        for d_id in self.drone_ids:
            path = self.astar(max_time)
            if path is None:
                raise PathNotFoundError(
                    f"No schedule found for {d_id} within {max_time} turns")
            self.reserve_path(path)
            self.add_moves(moves_by_turn, d_id, path)
            # print(f"{d_id}-{path}")
        # self.print_usage_by_turn()
        return dict(moves_by_turn)

    def successors(self, current: Node) -> list[tuple[str, int, int]]:
        """Legal moves from a node: (zone, arrival time, penalty added)."""
        result: list[tuple[str, int, int]] = []
        here = self.graph.get_zone(current.name)
        assert here is not None

        if not here.is_full(current.time + 1):
            result.append((current.name, current.time + 1, 0))

        for neighbor in self.graph.get_neighbors(current.name):
            turns = self.turns(neighbor)
            if turns is None:
                continue
            arrive = current.time + turns
            if self.is_move_safe(current.name, neighbor, current.time, arrive):
                extra = 0 if self.is_priority(neighbor) else 1
                result.append((neighbor, arrive, extra))
        return result

    def astar(self, max_depth: int) -> list[State] | None:
        """A* from start to end over (zone, time) states.

        States are ordered by (time + heuristic, non-priority count), so
        arrival time always wins and priority zones only break ties.

        Args:
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
                return self.rebuild(current)
            if current.time >= max_depth:
                continue

            for name, arrive, extra in self.successors(current):
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
    def rebuild(node: Node) -> list[State]:
        """Follow parents back to the root and return the path."""
        path: list[State] = []
        current: Node | None = node
        while current is not None:
            path.append((current.name, current.time))
            current = current.parent
        path.reverse()
        return path

    @staticmethod
    def add_moves(
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
