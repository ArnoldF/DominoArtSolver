from matplotlib import pyplot as plt

from src.preprocessing import compute_brightness_domino_diff


def draw_dots(ax, x, y, value, cell_width=1.0, cell_height=1.0):
    """
    Draw dots in a given field to represent the domino number value (0-9).
    """
    dot_positions = {
        0: [],
        1: [(0.5, 0.5)],
        2: [(0.2, 0.2), (0.8, 0.8)],
        3: [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)],
        4: [(0.2, 0.2), (0.2, 0.8), (0.8, 0.2), (0.8, 0.8)],
        5: [(0.2, 0.2), (0.2, 0.8), (0.5, 0.5), (0.8, 0.2), (0.8, 0.8)],
        6: [(0.3, 0.2), (0.3, 0.5), (0.3, 0.8), (0.7, 0.2), (0.7, 0.5), (0.7, 0.8)],
        7: [(0.2, 0.2), (0.2, 0.5), (0.2, 0.8), (0.5, 0.5), (0.8, 0.2), (0.8, 0.5), (0.8, 0.8)],
        8: [(0.2, 0.2), (0.2, 0.5), (0.2, 0.8), (0.5, 0.2), (0.5, 0.8), (0.8, 0.2), (0.8, 0.5), (0.8, 0.8)],
        9: [(0.2, 0.2), (0.2, 0.5), (0.2, 0.8), (0.5, 0.2), (0.5, 0.5), (0.5, 0.8), (0.8, 0.2), (0.8, 0.5), (0.8, 0.8)],
    }

    for dx, dy in dot_positions[value]:
        ax.add_patch(
            plt.Circle((y + dx * cell_width, x + dy * cell_height), 0.075, color='white')
        )


def create_solution_image(brightness_grid, solution, image_path: str) -> None:
    """
    Visualize the domino placement solution.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, len(brightness_grid[0]))
    ax.set_ylim(0, len(brightness_grid))

    # Formatting
    plt.axis("off")
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # Draw dominoes
    for domino, placement in solution:
        (x1, y1), (x2, y2) = placement

        # Draw domino boundary
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        ax.add_patch(
            plt.Rectangle(
                (y_min, x_min),
                y_max - y_min + 1,
                x_max - x_min + 1,
                color='#4b5a57',
                ec='black',
                lw=1
            )
        )

        # Draw dots for the two numbers in their respective fields
        brightness_field1 = brightness_grid[placement[0][0]][placement[0][1]]
        brightness_field2 = brightness_grid[placement[1][0]][placement[1][1]]
        if (
                compute_brightness_domino_diff(brightness_field1, brightness_field2, domino[0], domino[1]) <
                compute_brightness_domino_diff(brightness_field1, brightness_field2, domino[1], domino[0])
        ):
            # Place domino normally
            draw_dots(ax, x1, y1, domino[0])
            draw_dots(ax, x2, y2, domino[1])
        else:
            # Place domino reversed
            draw_dots(ax, x1, y1, domino[1])
            draw_dots(ax, x2, y2, domino[0])

    plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
