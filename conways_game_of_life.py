import os
import time


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


def print_grid(grid: list[list[bool]]) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    for y in range(len(grid[0])):
        for column in grid:
            if column[y]:
                print("██", end = "")
            else:
                print("\uffa0\uffa0", end = "")
        print()


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

    cell_grid = [[False if char == '0' else True for char in column] for column in transposed_text_grid]
    
    max_column_length = max([len(column) for column in cell_grid])

    padded_cell_grid = [column + [False for i in range(max_column_length - len(column))] for column in cell_grid]

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


def main():
    grid = read_grid(get_file_name())

    while True:
        gen_start_time = time.perf_counter_ns()
        print_grid(grid)

        grid = [[evaluate_cell(grid, x, y) for y in range(len(grid[0]))] for x in range(len(grid))]

        while time.perf_counter_ns() - gen_start_time < 250000000:
            pass


main()

