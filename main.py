import sys
from algo import PathNotFoundError, Pathfinder
from colors import Palette
from parser import Parser


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)
    try:
        parse = Parser()
        nb_drones, graph = parse.parse_map(sys.argv[1])
        pathfinder = Pathfinder(graph, nb_drones)
        moves = pathfinder.schedule_moves()
    except (PathNotFoundError, ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"Total turns: {len(moves)}")
    x: int = 1
    color: str = ""
    palette = Palette()
    for line in Pathfinder.format_output(moves):
        n_line = line.split()
        # print(f"Turn {x} : ", end="")
        for connection in n_line:
            n_connection = connection.split("-")
            drone = n_connection[0]
            zone_name = n_connection[1]
            color = graph.zones[zone_name].color
            print(f"{drone}-{palette.colorize(zone_name, color)} ", end="")
        print()
        x += 1
