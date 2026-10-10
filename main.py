import sys
from graph import Connection, Graph, Zone
from algo import PathNotFoundError, Pathfinder
from parser import parse_map


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)
    try:
        nb_drones, graph = parse_map(sys.argv[1])
        pathfinder = Pathfinder(graph, nb_drones)
        moves = pathfinder.schedule_moves()
    except (PathNotFoundError, ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("\n".join(moves))
    print(f"Total turns: {len(moves)}")
    for line in Pathfinder.format_output(moves):
        print(line)


if __name__ == "__main__":
    main()
