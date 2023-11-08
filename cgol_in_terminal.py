import os
import time


# Determines if a given cell on a grid will be alive or dead in the next generation.
def evaluate_cell(grid: list[list[bool]], cell_x: int , cell_y: int) -> bool:
    num_neighbours: int = 0

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
            if grid[x % len(grid)][y % len(grid[0])] is True:
                num_neighbours += 1

    # The rules of Conway's Game of Life state that a living cell will continue
    # living in the next generation if it has 2 or 3 neighbours, and that a dead
    # cell will come to life in the next generation if it has exactly 3 
    # neighbours. All cells that do not fit into one of these three descriptions
    # will be dead in the next generation.
    if grid[cell_x][cell_y] is True:
        if num_neighbours == 2 or num_neighbours == 3:
            return True
    else:
        if num_neighbours == 3:
            return True
    return False


# Clears the terminal output, then prints characters to represent cells.
def print_grid(grid: list[list[bool]]) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    # Grid is traversed column-by-row to properly print out to the terminal.
    for y in range(len(grid[0])):
        for column in grid:
            if column[y] is True:
                print("██", end = "")
            else:
                print("  ", end = "")
        print()


# Prompts a user for a positive number, then validates the input.
def get_pos_num(message: str = "") -> float:
    print(message, end = "")

    while True:
        user_in = input()

        # Periods have to be removed from the input when checking with isdigit 
        # because otherwise strings representing decimal numbers would not go 
        # through the filter. This means that we then also have to check that 
        # there isnt more than one period in the string.
        if user_in.replace('.', '').isdigit() and user_in.count('.') <= 1:
            if float(user_in) > 0:
                return float(user_in)

        print(f"\"{user_in}\" is not a valid input, try again: ", end = "")


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
        print(filename[-4:])
        filename += ".txt"

    return filename


# Reads a boolean grid from a .txt file.
def read_grid(file_path: str) -> list[list[bool]]:
    text_file = open(file_path)

    text_lines = [line.strip('\n')[::] for line in text_file]

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
    filename = input("Enter a file name: ")
    while filename[-4:] != ".txt":
        if '.' not in filename:
            filename = filename + ".txt"
            # Prevents the user from saving a grid as ".txt".
            if filename[-4:] != filename:
                break

        filename = input(f"{filename} is not a valid file name, try again: ")

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
    grid = read_grid(get_file_name())

    gen_frequency = get_pos_num("Enter a numerical value >0 for the generation frequency: ")

    while True:
        gen_start_time = time.perf_counter_ns()
        print_grid(grid)

        grid = [[evaluate_cell(grid, x, y) for y in range(len(grid[0]))] 
                for x in range(len(grid))]

        # Prevents the program from continuing until enough time has passed 
        # since the last generation was displayed.
        while time.perf_counter_ns() - gen_start_time < 1000000000 / gen_frequency:
            pass


main()

