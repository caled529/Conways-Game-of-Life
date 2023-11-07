import os
import pygame


def evaluate_cell(grid: list[list[bool]], cell_x: int , cell_y: int) -> bool:
    num_neighbours: int = 0

    for x in range(cell_x - 1, cell_x + 2):
        for y in range(cell_y - 1, cell_y + 2):
            if x == cell_x and y == cell_y:
                continue
            if grid[x % len(grid)][y % len(grid[0])]:
                num_neighbours += 1

    if grid[cell_x][cell_y]:
        if num_neighbours == 2 or num_neighbours == 3:
            return True
    else:
        if num_neighbours == 3:
            return True
    return False


def render_grid(screen: pygame.Surface, grid: list[list[bool]], cell_size: int) -> None:
    BLACK = pygame.Color(0, 0, 0)
    GREY = pygame.Color(127, 127, 127)

    for y in range(len(grid[0])):
        for x in range(len(grid)):
            cell_rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)

            if grid[x][y]:
                pygame.draw.rect(screen, BLACK, cell_rect)
            else:
                pygame.draw.rect(screen, GREY, cell_rect)

            pygame.draw.rect(screen, BLACK, cell_rect, 1)

    pygame.display.flip()


def get_file_name() -> str:
    options = []
    for file in os.listdir():
        if file[-4:] == ".txt":
            options.append(file)

    print("Select one of the following to open as a grid:")
    for index, file in enumerate(options):
        print(index + 1, "-", file)

    while True:
        filename = input().strip()

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

    if filename[-4:] != ".txt":
        print(filename[-4:])
        filename += ".txt"

    return filename


def read_grid(file_path: str) -> list[list[bool]]:
    text_file = open(file_path)

    text_lines = [line.strip('\n')[::] for line in text_file]

    max_line_length = max([len(line) for line in text_lines])

    padded_text_lines = [line + (max_line_length - len(line)) * '0' for line in text_lines]

    transposed_text_grid = zip(*padded_text_lines)

    cell_grid = [[False if char == '0' else True for char in column] 
                 for column in transposed_text_grid]
    
    max_column_length = max([len(column) for column in cell_grid])

    padded_cell_grid = [column + [False for i in range(max_column_length - len(column))] 
                        for column in cell_grid]

    print(f"Loaded file \"{file_path}\"")

    return padded_cell_grid


def write_grid(grid: list[list[bool]]) -> None:
    filename = input("Enter a file name: ")
    while filename[-4:] != ".txt":
        if '.' not in filename:
            filename = filename + ".txt"
            if filename[-4:] != filename:
                break
        filename = input(f"{filename} is not a valid file name, try again")

    new_file = open(filename, 'w')

    transposed_grid = zip(*grid)

    for line in transposed_grid:
        for state in line:
            new_file.write('1' if state == True else '0')
        new_file.write('\n')

    new_file.close()

    print(f"Grid saved to \"{filename}\"")


def main():
    GEN_FREQUENCY = 5
    WIN_SIZE_RATIO = 0.90

    pygame.init()

    SCREEN_WIDTH = pygame.display.Info().current_w
    SCREEN_HEIGHT = pygame.display.Info().current_h

    grid = read_grid(get_file_name())

    cell_size = int(min(SCREEN_WIDTH * WIN_SIZE_RATIO / len(grid), 
                        SCREEN_HEIGHT * WIN_SIZE_RATIO / len(grid[0])))

    screen = pygame.display.set_mode((len(grid) * cell_size, len(grid[0]) * cell_size))

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

