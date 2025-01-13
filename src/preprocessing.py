import logging


logger = logging.getLogger(__name__)


def find_valid_row_col_combination(num_domino_sets: int, aspect_ratio: float) -> tuple[int, int]:
    """
    Search for a combination of cols m and rows n such that mn=110s where s=`num_domino_sets`
    Each Domino set is assumed to have 55 tiles, and thus covers 110 fields.
    The combination should be close to the given aspect ratio
    """
    num_fields = 110 * num_domino_sets

    options = []
    cols = 1
    while cols <= num_fields:
        # are the resulting rows an integer
        rows = num_fields / cols
        if int(rows) == rows:
            options.append((int(rows), cols))
        cols += 1

    if not options:
        raise ValueError('No combination of rows and cols could be found.')

    # sort by deviation from aspect ratio
    sorted_options = sorted(options, key=lambda x: abs((x[1] / x[0]) - aspect_ratio))

    return sorted_options[0]


def create_domino_tiles(max_num: int = 9) -> dict[int, tuple[int, int]]:
    domino_list = []

    for i in range(max_num + 1):
        for j in range(i, max_num + 1):
            domino_list.append((i, j))

    # Assign an Id to each domino tile
    domino_tiles = {
        _id: _numbers for _id, _numbers in enumerate(domino_list)
    }

    return domino_tiles


def generate_placements(rows: int, cols: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Generate all possible options to place a domino on the grid.
    Dominos can be placed horizontally and vertically
    """
    placements = []

    for x in range(rows):
        for y in range(cols):
            # Horizontal placement
            if y + 1 < cols:
                placements.append(((x, y), (x, y + 1)))
            # Vertical placement
            if x + 1 < rows:
                placements.append(((x, y), (x + 1, y)))

    return placements


def compute_brightness_domino_diff(
        brightness_field1: float,
        brightness_field2: float,
        digit1: int,
        digit2: int
) -> float:
    return int((brightness_field1 - digit1) ** 2 + (brightness_field2 - digit2) ** 2)


def compute_diff_placement_domino(
        brightness_grid,
        domino_set: dict[int, tuple[int, int]],
        placements: list[tuple[tuple[int, int], tuple[int, int]]]
):
    diff_placement_domino = dict()
    for tile, (number1, number2) in domino_set.items():
        for place in placements:
            brightness_field1 = brightness_grid[place[0][0]][place[0][1]]
            brightness_field2 = brightness_grid[place[1][0]][place[1][1]]

            # since we can place the domino also reversely, take the minimum of both options
            diff_placement_domino[(tile, place)] = min(
                compute_brightness_domino_diff(
                    brightness_field1, brightness_field2, number1, number2),
                compute_brightness_domino_diff(
                    brightness_field1, brightness_field2, number2, number1)
            )

    return diff_placement_domino

