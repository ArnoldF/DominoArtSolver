import itertools
import logging

import pulp


logger = logging.getLogger(__name__)


class DominoModel:
    _milp_model: pulp.LpProblem

    def __init__(
            self,
            diff_placement_domino: list[list[float]],
            domino_tiles: dict[int, tuple[int, int]],
            placements: list[tuple[tuple[int, int], tuple[int, int]]],
            sets: int,
            rows: int,
            cols: int
    ):
        self.diff_placement_domino = diff_placement_domino
        self._rows = rows
        self._cols = cols
        self._domino_tiles = domino_tiles
        self._placements = placements
        self._sets = sets

        self._milp_model = pulp.LpProblem("DominoPlacement", pulp.LpMinimize)

        self._variables = self._create_variables()
        self._create_objectives()
        self._create_constraints()

        #self.construct_warm_start()

    def _create_variables(self):
        # Define binary variables for each combination of domino and placement
        variables = dict()

        variables['domino_at_place'] = pulp.LpVariable.dicts(
            "domino_at_place",
            ((domino, place)
             for domino in self._domino_tiles.keys()
             for place in self._placements),
            cat="Binary"
        )
        return variables

    def _create_objectives(self) -> None:
        # Minimize the difference between the brightness of a field and the digits on the assigned domino tile
        diff_brightness_numbers = pulp.lpSum(
            self._variables["domino_at_place"][domino, place] * self.diff_placement_domino[domino, place]
            for domino in self._domino_tiles.keys()
            for place in self._placements
        )

        self._milp_model.setObjective(diff_brightness_numbers)

    def _create_constraints(self):
        # Constraint 1: Each field / place must be covered exactly once
        for x, y in itertools.product(range(self._rows), range(self._cols)):
            count_field_is_covered = pulp.lpSum(
                self._variables["domino_at_place"][domino, place]
                for domino in self._domino_tiles.keys()
                for place in self._placements
                if (x, y) in place
            )

            self._milp_model.addConstraint(
                count_field_is_covered == 1,
                f"cover_field_once_{x}_{y}"
            )

        # Constraint 2: Each domino must be used exactly once
        for domino in self._domino_tiles.keys():
            count_domino_usage = pulp.lpSum(
                self._variables["domino_at_place"][domino, place]
                for place in self._placements
            )
            self._milp_model.addConstraint(
                count_domino_usage == self._sets,
                f"use_domino_once_{domino}"
            )

    def solve(self) -> list:
        self._milp_model.solve(
            pulp.PULP_CBC_CMD(
                msg=True,
                mip=True
            )
        )

        logger.info(f'Solved model with status {self._milp_model.status}')

        # Format the results
        solution = []
        for domino_id, domino_values in self._domino_tiles.items():
            for place in self._placements:
                if pulp.value(self._variables["domino_at_place"][(domino_id, place)]) == 1:
                    solution.append((domino_values, place))

        if len(solution) != len(self._domino_tiles) * self._sets:
            logger.error(
                f'Placed {len(solution)} tiles, but {len(self._domino_tiles) * self._sets} are given.'
            )

        return solution


    def construct_warm_start(self):
        warm_start_solution = {}

        # if the number of column is even, use all horizontal placements
        if self._cols % 2 == 0:
            placements = [((x, y), (x, y + 1)) for x in range(self._rows) for y in range(self._cols - 1)]
        else:  # use all vertical placements
            placements = [((x, y), (x + 1, y)) for x in range(self._rows) for y in range(self._cols)]

        # Compute brightness for each placement
        placement_brightness = {
            p: self._brightness_grid[p[0][0]][p[0][1]] + self._brightness_grid[p[1][0]][p[1][1]]
            for p in placements
        }

        # Sort placements by brightness in descending order
        sorted_placements = sorted(
            placement_brightness.items(),
            key=lambda item: item[1],
            reverse=True
        )

        # Sort domino tiles by the sum of numbers on both sides in descending order
        sorted_dominoes = sorted(
            self._domino_tiles.items(),
            key=lambda item: sum(item[1]),
            reverse=True
        )

        # Keep track of used placements and tiles
        used_placements = set()
        used_dominoes = set()

        # Assign tiles to placements
        for domino, (num1, num2) in sorted_dominoes:
            for placement, _ in sorted_placements:
                if placement not in used_placements:
                    warm_start_solution[(domino, placement)] = 1
                    used_placements.add(placement)
                    used_dominoes.add(domino)
                    break

        # Fill in 0 for unused domino-placement pairs
        for domino in self._domino_tiles:
            for placement in placements:
                if (domino, placement) not in warm_start_solution:
                    warm_start_solution[(domino, placement)] = 0

        # Apply the warm start solution to the variables
        for (domino, place), value in warm_start_solution.items():
            self._variables["domino_at_place"][domino, place].setInitialValue(value)

        # return warm_start_solution
