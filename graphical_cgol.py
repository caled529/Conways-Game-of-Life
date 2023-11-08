import os
import pygame


# Determines if a given cell on a grid will be alive or dead in the next generation.
def evaluate_cell(grid: list[list[bool]], cell_x: int , cell_y: int) -> bool:
    num_neighbours = 0

    # Look at all the cells adjacent to the current cell and increase the
    # neighbour counter for each living cell.
    for x in range(cell_x - 1, cell_x + 2):
        for y in range(cell_y - 1, cell_y + 2):
            if x == cell_x and y == cell_y:
                continue
            # The use of mod here allows the cells to be less restricted in 
            # their growth by permitting looping around to the other side of the 
            # grid. One could think of it like how world maps are projections of
            # a 3D sphere onto a 2D plane.
            if grid[x % len(grid)][y % len(grid[0])]:
                num_neighbours += 1

    # The rules of Conway's Game of Life state that a living cell will continue
    # living in the next generation if it has 2 or 3 neighbours, and that a dead
    # cell will come to life in the next generation if it has exactly 3 
    # neighbours. All cells that do not fit into one of these three descriptions
    # will be dead in the next generation.
    if grid[cell_x][cell_y]:
        if num_neighbours == 2 or num_neighbours == 3:
            return True
    else:
        if num_neighbours == 3:
            return True
    return False


# Draws the grid of cells onto a pygame window.
def render_grid(screen: pygame.Surface, grid: list[list[bool]], cell_size: int) -> None:
    BLACK = pygame.Color(0, 0, 0)
    GREY = pygame.Color(127, 127, 127)

    for x in range(len(grid)):
        for y in range(len(grid[x])):
            cell_rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)

            # Draw a black square for living cells, and a grey one for dead cells.
            if grid[x][y]:
                pygame.draw.rect(screen, BLACK, cell_rect)
            else:
                pygame.draw.rect(screen, GREY, cell_rect)

            # Draw an empty square with a black outline to represent gridlines.
            pygame.draw.rect(screen, BLACK, cell_rect, 1)

    pygame.display.flip()


# Prompts the user to select from all .txt files in the current directory, then
# does some input correction to ensure they pick a valid file.
def get_file_name() -> str:
    # Get the list of .txt files in the current directory.
    options = [file for file in os.listdir() if file[-4:] == ".txt"]

    print("Select one of the following to open as a grid:")
    for index, file in enumerate(options):
        print(index + 1, "-", file)

    while True:
        filename = input().strip()

        # Allows the user to select files with numbers.
        if filename.isdigit():
            if int(filename) in range(1, len(options) + 1):
                filename = options[int(filename) - 1]
                break
            print(filename, "is not a valid file selection, try again: ", end ="")
            continue

        if filename not in options:
            if filename + ".txt" in options:
                break
            print(filename, "is not a valid file selection, try again: ", end ="")
            continue

    # Since filenames without the .txt extension are accepted, the extension
    # must be added before returning the filename. 
    if filename[-4:] != ".txt":
        filename += ".txt"

    return filename


# Reads a boolean grid from a .txt file.
def read_grid(file_path: str) -> list[list[bool]]:
    text_file = open(file_path)

    text_lines = [line.strip('\n') for line in text_file]

    max_line_length = max([len(line) for line in text_lines])

    # Strings from the text file are padded to force each row of the grid to be
    # the same length.
    padded_text_lines = [line + (max_line_length - len(line)) * '0' for line in text_lines]

    # Transposes the text matrix to allow the characters to be parsed row-by-column.
    transposed_text_grid = zip(*padded_text_lines)

    # 0s are parsed as dead cells, while all other characters are parsed as living cells.
    cell_grid = [[False if char == '0' else True for char in column] 
                 for column in transposed_text_grid]
    
    print(f"Loaded file \"{file_path}\"")

    return cell_grid


# Saves the current state of the grid to a text file of the user's choice.
def write_grid(grid: list[list[bool]]) -> None:
    filename = input("Enter a file name: ").strip()
    while filename[-4:] != ".txt":
        if '.' not in filename:
            filename = filename + ".txt"
            # Prevents the user from saving a grid as ".txt".
            if filename[-4:] != filename:
                break

        filename = input(f"{filename} is not a valid file name, try again")

    new_file = open(filename, 'w')

    # Transpose the grid to parse it line by line and write out to a text file.
    transposed_grid = zip(*grid)

    for line in transposed_grid:
        for state in line:
            new_file.write('1' if state == True else '0')
        new_file.write('\n')

    new_file.close()

    print(f"Grid saved to \"{filename}\"")


def main():
    GEN_FREQUENCY = 4
    WIN_SIZE_RATIO = 0.90

    pygame.init()

    SCREEN_WIDTH = pygame.display.Info().current_w
    SCREEN_HEIGHT = pygame.display.Info().current_h

    grid = read_grid(get_file_name())

    # Scale the cell size off of the user's display.
    cell_size = int(min(SCREEN_WIDTH * WIN_SIZE_RATIO / len(grid), 
                        SCREEN_HEIGHT * WIN_SIZE_RATIO / len(grid[0])))

    screen = pygame.display.set_mode((len(grid) * cell_size, len(grid[0]) * cell_size))

    render_grid(screen, grid, cell_size)

    clock = pygame.time.Clock()
    millis_since_last_gen = 0

    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False                

            if event.type == pygame.KEYDOWN:
                match event.key:
                    
                    case pygame.K_SPACE:
                        paused = not paused

                    case pygame.K_o | pygame.K_r:
                        grid = read_grid(get_file_name())
                        # Dynamically scales the cell and window size when a new 
                        # grid is opened from a file.
                        cell_size = int(min(SCREEN_WIDTH * WIN_SIZE_RATIO / len(grid),
                                            SCREEN_HEIGHT * WIN_SIZE_RATIO / len(grid[0])))
                        screen = pygame.display.set_mode((len(grid) * cell_size, 
                                                          len(grid[0]) * cell_size))
                        render_grid(screen, grid, cell_size)

                    case pygame.K_s | pygame.K_w:
                        write_grid(grid)

                    case pygame.K_ESCAPE:
                        running = False
         
        millis_since_last_gen += clock.tick(60)
        if millis_since_last_gen >= 1000 / GEN_FREQUENCY and not paused:
            millis_since_last_gen = 0
            grid = [[evaluate_cell(grid, x, y) for y in range(len(grid[x]))] 
                    for x in range(len(grid))]
            render_grid(screen, grid, cell_size)
            

main()

