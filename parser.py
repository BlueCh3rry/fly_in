

def map_path() -> str:
    return ""


def parser_txt() -> None:
    try:
        with open(map_path(), "r", encoding="utf-8") as txt_file:
            drone
            for line in txt_file:
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones"):
                elif line.startswith("start_hub"):
                elif line.startswith("end_hub"):
                elif line.startswith("hub"):
                elif line.startswith("connection"):
                else:
                    print(f"line not good:\n'{line}'\n")

    except Exception:
        raise Exception("Cant open file txt ")