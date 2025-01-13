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
