from tools import Drone, Zone, Data

def map_path() -> str:
    return "" # path will be added later


def parser_txt() -> Data:
    try:
        with open(map_path(), "r", encoding="utf-8") as txt_file:
            data = Data()
            for line in txt_file:
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones"):
                    lst_drone = [Drone(i, [0, 0]) for i in range()]
                elif line.startswith("start_hub"):
                    data.start = Zone()
                elif line.startswith("end_hub"):
                    data.start = Zone()
                elif line.startswith("hub"):
                    lst_zone = Zone()
                elif line.startswith("connection"):

                else:
                    print(f"line not good:\n'{line}'\n")
        data.drones = tuple(lst_drone)
        data.zones = tuple(lst_zone)
    except Exception as e:
        raise Exception(f"Cant open file txt: {e}")
