"""Printing helpers. Reads a Graph, never owns data."""

from colors import colorize
from graph import Graph, Zone


def _zone_line(graph: Graph, zone: Zone) -> str:
    name = colorize(zone.name, zone.color) if zone.color else zone.name
    return (f"\tname = {name}"
            f"\tcoord = ({zone.x}, {zone.y})"
            f"\tcolor = {zone.color}"
            f"\ttype = {zone.zone_type.value}"
            f"\tneighbors = {graph.get_neighbors(zone.name)}"
            f"\tmax_drones = {zone.max_drones}")


def show_zone(graph: Graph, name: str) -> None:
    """Print one zone."""
    print("Zone info, 'show_zone()':")
    zone = graph.get_zone(name)
    print(_zone_line(graph, zone) if zone else f"\tunknown zone '{name}'")


def show_all_zones(graph: Graph) -> None:
    """Print every zone."""
    print("All zones info, 'show_all_zones()':")
    for zone in graph.get_all_zones():
        print(_zone_line(graph, zone))


def show_connection(graph: Graph, z1: str, z2: str) -> None:
    """Print one connection."""
    print("Connection info, 'show_connection()':")
    conn = graph.get_connection(z1, z2)
    if conn is None:
        print(f"\tno connection {z1}-{z2}")
        return
    print(f"\t{conn.zone1}-{conn.zone2}"
          f"\tmax link capacity = {conn.max_link_capacity}")


def show_all_connections(graph: Graph) -> None:
    """Print every connection once (the dict stores both directions)."""
    print("All connections info, 'show_all_connections()':")
    seen = set()
    for conn in graph.connections.values():
        if id(conn) in seen:
            continue
        seen.add(id(conn))
        print(f"\t{conn.zone1}-{conn.zone2}"
              f"\tmax link capacity = {conn.max_link_capacity}")
