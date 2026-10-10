"""Map file parser: builds a Graph from the map format."""

import re

from graph import Connection, Graph, Zone

LINE_RE = re.compile(r"^(\w+):\s*(.*?)\s*(?:\[(.*)\])?$")

HUB_KINDS = ("start_hub", "hub", "end_hub")
ZONE_KEYS = {"zone", "color", "max_drones"}
LINK_KEYS = {"max_link_capacity"}

DEFAULT_ZONE_TYPE = "normal"
DEFAULT_COLOR = "white"
DEFAULT_LINK_CAPACITY = 1


def parse_meta(raw: str | None, allowed: set[str]) -> dict[str, str]:
    """Parse 'key=value key=value' and reject unknown or malformed items.

    Metadata is optional: a missing or empty block returns an empty dict.
    """
    meta: dict[str, str] = {}
    for item in (raw or "").split():
        key, sep, value = item.partition("=")
        if not sep or not value:
            raise ValueError(f"bad metadata '{item}', expected key=value")
        if key not in allowed:
            raise ValueError(f"unknown metadata key '{key}'")
        meta[key] = value
    return meta


def parse_hub(body: str, meta: dict[str, str], default_size: int) -> Zone:
    """Build a Zone from '<name> <x> <y>' plus its (optional) metadata."""
    parts = body.split()
    if len(parts) != 3:
        raise ValueError(f"expected '<name> <x> <y>', got '{body}'")
    name, x, y = parts
    # if not name.isalnum():
    #     raise ValueError(f"zone name must be alphanumeric: '{name}'")
    return Zone(
        name, int(x), int(y),
        zone_type=meta.get("zone", DEFAULT_ZONE_TYPE),
        color=meta.get("color") or DEFAULT_COLOR,
        max_drones=int(meta.get("max_drones", default_size)),
    )


def parse_map(path: str) -> tuple[int, Graph]:
    """Read a map file and return (nb_drones, graph).

    Raises:
        OSError: the file cannot be read.
        ValueError: the content is invalid (message includes the line).
    """
    graph = Graph()
    nb_drones: int | None = None
    links: list[tuple[str, str, int, int]] = []
    coords: dict[tuple[int, int], str] = {}

    with open(path, encoding="utf-8") as f:
        for num, raw_line in enumerate(f, 1):
            line = raw_line.split("#")[0].strip()
            if not line:
                continue
            try:
                m = LINE_RE.match(line)
                if not m:
                    raise ValueError(f"bad line '{line}'")
                key, body, raw_meta = m.groups()

                if key == "nb_drones":
                    if nb_drones is not None:
                        raise ValueError("duplicate nb_drones")
                    parse_meta(raw_meta, set())
                    nb_drones = int(body)
                    if nb_drones <= 0:
                        raise ValueError("nb_drones must be positive")

                elif key in HUB_KINDS:
                    if nb_drones is None:
                        raise ValueError("nb_drones must come first")
                    if key == "start_hub" and graph.start_hub is not None:
                        raise ValueError("duplicate start_hub")
                    if key == "end_hub" and graph.end_hub is not None:
                        raise ValueError("duplicate end_hub")
                    meta = parse_meta(raw_meta, ZONE_KEYS)
                    size = 1 if key == "hub" else nb_drones
                    zone = parse_hub(body, meta, size)

                    # parse_hub succeeded, so body is '<name> <x> <y>'
                    _, x, y = body.split()
                    pos = (int(x), int(y))
                    if pos in coords:
                        raise ValueError(
                            f"zones '{coords[pos]}' and '{zone.name}' "
                            f"share the same coordinates {pos}")
                    coords[pos] = zone.name

                    graph.add_zone(zone)
                    if key == "start_hub":
                        graph.start_hub = zone
                    elif key == "end_hub":
                        graph.end_hub = zone

                elif key == "connection":
                    meta = parse_meta(raw_meta, LINK_KEYS)
                    names = body.split("-")
                    if len(names) != 2 or names[0] == names[1]:
                        raise ValueError(
                            f"expected '<name1>-<name2>', got '{body}'")
                    links.append((
                        names[0], names[1],
                        int(meta.get("max_link_capacity",
                                     DEFAULT_LINK_CAPACITY)),
                        num))
                else:
                    raise ValueError(f"unknown line type '{key}'")
            except ValueError as err:
                raise ValueError(f"line {num}: {err}") from None

    if nb_drones is None:
        raise ValueError("missing nb_drones")
    if graph.start_hub is None:
        raise ValueError("missing start_hub")
    if graph.end_hub is None:
        raise ValueError("missing end_hub")

    # connections need both zones to exist, so add them last
    for a, b, cap, num in links:
        try:
            graph.add_connection(Connection(a, b, cap))
        except ValueError as err:
            raise ValueError(f"line {num}: {err}") from None
    return nb_drones, graph
