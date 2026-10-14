*This project has been created as part of the 42 curriculum by mmakhmae*

## Description

The goal of the Fly-in project is to simulate the movement of drones through a network of interconnected zones, guiding them from a starting hub to a destination hub while respecting the constraints of the network.

Each zone represents a location in the network, and each connection represents a possible route between two zones. Drones must navigate this network while respecting zone capacities, connection capacities, movement durations, and blocked zones.

The challenge is to find valid routes for all drones while minimizing the total number of simulation turns.

To solve this problem, the project implements a capacity-aware A* pathfinding algorithm combined with a reservation-table scheduling system. Drones are scheduled sequentially, and each planned route reserves the zones and connections it uses at specific turns. Subsequent drones must find routes that respect these existing reservations.

The project also supports different zone types, allowing the simulation to represent priority routes, restricted passages, and inaccessible areas.

## Instructions

### Execution

```bash
    make run
    or
    uv run python3 main.py path/to/map.txt
```


### Available Operations

```bash
    make install
    make run
    make debug
    make lint
    make lint-strict
```

## Algorithm Choices & Justification

### A* Pathfinding

The project uses A* to find the earliest-arrival route for each drone.

The algorithm evaluates states using:

**f(n) = g(n) + h(n)**

- `g(n)`: Elapsed simulation turns.
- `h(n)`: Estimated minimum turns remaining to reach the destination.
- `f(n)`: Estimated total arrival time.

Each state is represented by `(zone_name, time)`, allowing the algorithm to account for capacity constraints and waiting.

The heuristic is calculated using reverse Dijkstra, considering the movement cost of each zone. Restricted zones cost two turns, while normal and priority zones cost one. Blocked zones are excluded.

### Dijkstra's Algorithm for the Heuristic

The heuristic used by A* is calculated using **Reverse Dijkstra's algorithm**, starting from the destination hub.

Dijkstra explores the graph to calculate the minimum travel cost from each zone to the destination. The movement cost depends on the zone type:

- `normal`: 1 turn.
- `priority`: 1 turn.
- `restricted`: 2 turns.
- `blocked`: Inaccessible.

These distances provide A* with an estimate of the remaining travel time, helping it explore promising routes first.

The heuristic ignores dynamic reservations, making it an optimistic estimate that guides the search efficiently.

### Priority-Based Routing

When candidate states have the same estimated arrival cost, the algorithm prefers routes with fewer non-priority zones.

This encourages drones to use priority zones without sacrificing the primary objective of minimizing arrival time.

### Resources

Documentation & Guides,
Official 42 subject,
pathfinder algorithm forums,
geeksforgeeks.org

### AI Usage

AI was used in this project for:
Understanding and comparing different sorting strategies,
Clarifying algorithm optimization techniques,
Helping to find bugs,
Refining readme.
