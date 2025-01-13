import logging
import os

from src.domino_model import DominoModel
from src.image_processing import ImageReader
from src.plotting import create_solution_image
from src.preprocessing import find_valid_row_col_combination, create_domino_tiles, generate_placements, \
    compute_diff_placement_domino

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DOMINO_SETS_USED = 18
IMAGE_FILE = "Einsten.jpg"

logger.info('Converting image to greyscale.')
image_reader = ImageReader(image_path=os.path.join('images', 'input', IMAGE_FILE))

logger.info('Finding suitable dimensions for grid.')
rows, cols = find_valid_row_col_combination(
    num_domino_sets=DOMINO_SETS_USED,
    aspect_ratio=image_reader.aspect_ratio
)

logger.info('Creating domino set.')
domino_tiles = create_domino_tiles()

logger.info('Computing brightness grid.')
brightness_grid = image_reader.get_field_brightness(grid_size=(rows, cols))

logger.info('Generating all possible placements.')
placements = generate_placements(rows=rows, cols=cols)

logger.info('Computing brightness distance between placements and dominos.')
diff_placement_domino = compute_diff_placement_domino(
    brightness_grid=brightness_grid,
    domino_set=domino_tiles,
    placements=placements
)

logger.info('Building MILP model.')
model = DominoModel(
    diff_placement_domino=diff_placement_domino,
    domino_tiles=domino_tiles,
    placements=placements,
    sets=DOMINO_SETS_USED,
    rows=rows,
    cols=cols
)
logger.info('Solving MILP model.')
solution = model.solve()

logger.info('Creating result image.')
output_file = f'{IMAGE_FILE.split(".")[0]}_{DOMINO_SETS_USED}_sets.png'
output_path = os.path.join('images', 'output', output_file)
create_solution_image(brightness_grid, solution, output_path)
