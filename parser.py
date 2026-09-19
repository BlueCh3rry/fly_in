from tools import Drone, Zone, Zone_queue, Data, colors


def map_path() -> str:
    return "/home/mmakhmae/42cursus/fly_in/arg.txt"
    # return "C:/Users/Red/home/42Cursus/fly_in/arg.txt"


def exract_line(line: list[str], arg: int) -> dict[str, str | None]:
    line[0] = line[0].strip("[")
    line[len(line) - 1] = line[len(line) - 1].strip("]")
    n_line: dict[str, str | None] = {"zone": None,
                                     "color": None,
                                     "max_drones": None,
                                     "max_link_capacity": None}
    for elem in line:
        if elem.startswith("zone") and arg == 2:
            n_line["zone"] = elem.split("=")[1].strip()
        elif elem.startswith("color") and arg != 3:
            n_line["color"] = elem.split("=")[1].strip()
        elif elem.startswith("max_drones") and arg == 2:
            n_line["max_drones"] = elem.split("=")[1].strip()
        elif elem.startswith("max_link_capacity") and arg == 3:
            n_line["max_link_capacity"] = elem.split("=")[1].strip()
        else:
            print(f"(1) skipping this data, not good: {elem}")
    return n_line


def check_line_valid(parts: list[str]) -> tuple[str, int, int]:
    if len(parts) < 4:
        raise Exception("Not enough parameters")
    try:
        name = parts[1]
        if not name.isalnum():
            raise ValueError("name must be alphanumeric")
        x = int(parts[2])
        y = int(parts[3])
        return name, x, y
    except (IndexError, ValueError) as e:
        raise Exception(f"ERR : Line is not good shape: {e}")


def apply_links(lst_links: list[list[str]], target: list[Zone]) -> None:
    for zone in target:
        zone.links = tuple((link[0], link[1])
                           for link in lst_links if zone.name in link)


def parser_txt() -> Data:
    try:
        with open(map_path(), "r", encoding="utf-8") as txt_file:
            start_done = 0
            end_done = 0
            lst_zones: list[Zone] = []
            lst_queues: list[Zone_queue] = []
            lst_zone_name: list[str] = []
            lst_links: list[list[str]] = []
            for line in txt_file:
                metadata: dict[str, str | None] = {"zone": None,
                                                   "color": None,
                                                   "max_drones": None,
                                                   "max_link_capacity": None}
                if line.startswith("#") or line.isspace():
                    continue
                if line.startswith("nb_drones"):
                    nb_drones = int(line.split(":")[1].strip())
                    lst_drones = []
                    for i in range(nb_drones):
                        lst_drones.append(Drone(id=i, location=[0, 0]))
                if line.startswith("start_hub") and start_done == 0:
                    parts = line.split()
                    name, x, y = check_line_valid(parts)
                    lst_zone_name.append(name)
                    metadata = exract_line(parts[4:], 1)
                    start = Zone(name=name,
                                 coord=(x, y),
                                 color=colors[metadata["color"]
                                              if metadata["color"] is not None
                                              else ''],
                                 status=metadata["zone"],
                                 links=None,
                                 max_drones=int(metadata["max_drones"]
                                                if metadata["max_drones"]
                                                is not None else nb_drones))
                    start_done = 1
                if line.startswith("end_hub") and end_done == 0:
                    parts = line.split()
                    name, x, y = check_line_valid(parts)
                    lst_zone_name.append(name)
                    metadata = exract_line(parts[4:], 1)
                    end = Zone(name=name,
                               coord=(x, y),
                               color=colors[metadata["color"]
                                            if metadata["color"] is not None
                                            else ''],
                               status=metadata["zone"],
                               links=None,
                               max_drones=int(metadata["max_drones"]
                                              if metadata["max_drones"]
                                              is not None else nb_drones))
                    end_done = 1
                if line.startswith("hub"):
                    parts = line.split()
                    name, x, y = check_line_valid(parts)
                    lst_zone_name.append(name)
                    metadata = exract_line(parts[4:], 2)
                    hub = Zone(name=name,
                               coord=(x, y),
                               color=colors[metadata["color"]
                                            if metadata["color"] is not None
                                            else ''],
                               status=metadata["zone"],
                               links=None,
                               max_drones=int(metadata["max_drones"]
                                              if metadata["max_drones"]
                                              is not None else nb_drones))
                    lst_zones.append(hub)
                if line.startswith("connection:"):
                    parts = line.split()
                    name = parts[1]
                    lst_name_connection = name.split("-")
                    if (len(lst_name_connection) != 2 or
                       (lst_name_connection[0] not in lst_zone_name or
                       lst_name_connection[1] not in lst_zone_name)):
                        raise ValueError("connections name are not correct,"
                                         " expected: '<name1>-<name2>' got :",
                                         lst_name_connection)
                    lst_links.append(lst_name_connection)
                    if len(parts) == 3:
                        metadata = exract_line([parts[2]], 3)
                    queue = Zone_queue(drones_waiting_nbr=0,
                                       drones_lst=[],
                                       max_link_capacity=int(
                                           metadata["max_link_capacity"]
                                           if metadata["max_link_capacity"]
                                           is not None else 1),
                                       zone_location=(lst_name_connection[0],
                                                      lst_name_connection[1]))
                    lst_queues.append(queue)
                if not (line.startswith("nb_drones:") or
                        line.startswith("start_hub:") or
                        line.startswith("end_hub:") or
                        line.startswith("hub:") or
                        line.startswith("connection:")):
                    raise ValueError(f"Error, this line not good: '{line}'\n")
        apply_links(lst_links, [start])
        apply_links(lst_links, [end])
        apply_links(lst_links, lst_zones)
        data = Data(drones=nb_drones, start=start, end=end,
                    zones=tuple(lst_zones), lst_drones=tuple(lst_drones),
                    zone_queues=tuple(lst_queues))
    except Exception as e:
        raise Exception(f"Got error: {e}")
    return data
