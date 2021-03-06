# Random Maze Generator using Depth-first Search
# http://en.wikipedia.org/wiki/Maze_generation_algorithm

# Code from http://code.activestate.com/recipes/578356-random-maze-generator/
# FB - 20121214
# Modified by Peter O'Conor

from mpl_toolkits.axes_grid1 import ImageGrid
from scipy.ndimage.measurements import label
from matplotlib import pyplot as plt
import numpy as np
import argparse
import torch
import os

ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))


def base_check_maze(maze: np.ndarray) -> bool:
    """Checks whether the input is a valid maze. Checks the following:
            * there are no islands (i.e. there are no loops).
            * all white pixels are connected.

        Args:
            maze:  The maze to be evaluated

        Returns:
            Whether the maze is valid or not.
        """
    # single connected-component
    labeled_array, num_features = label(maze)

    npmaze = np.array(maze)
    mx, my = npmaze.shape
    if num_features > 1:
        return False
    # no loops
    for i in range(mx - 1):
        for j in range(my - 1):
            if maze[i, j] == 1:
                if maze[i + 1, j] == 1 and maze[i, j + 1] == 1 and maze[i + 1, j + 1] == 1:
                    return False
    maze = maze - 1
    s = [[1, 1, 1],
         [1, 1, 1],
         [1, 1, 1]]
    labeled_array, num_features = label(maze, structure=s)
    for feat in range(1, num_features + 1):
        indexes = np.array(np.where(labeled_array == feat))
        if np.all(indexes[:, :] != 0) and np.all(indexes[0, :] != mx - 1) and np.all(indexes[1, :] != my - 1):
            return False
    return True


def gen_maze(mx: int, my: int) -> np.ndarray:
    """Generate a shape (mx, my) maze.  1's represent "hallways" and 0's represent "walls".
    All "hallways" will be connected into a single component with no loops.

    This does not take care of setting appropriate (start/stop) pixels.  Any white pixel could be used as a start/end
    point.

    Args:
        mx: The length of the maze.
        my: The height of the maze.

    Returns:
        A maze of size mx by my.
    """
    maze = np.zeros((my, mx), dtype=np.bool)
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]  # 4 directions to move in the maze
    stack = [(np.random.randint(0, mx), np.random.randint(0, my))]

    while len(stack) > 0:
        (cx, cy) = stack[-1]
        maze[cy][cx] = 1
        nlst = []  # list of available neighbors
        for i in range(4):
            nx = cx + dx[i]
            ny = cy + dy[i]
            if 0 <= nx < mx and 0 <= ny < my:
                if maze[ny][nx] == 0:
                    # of occupied neighbors must be 1
                    ctr = 0
                    for j in range(4):
                        ex = nx + dx[j]
                        ey = ny + dy[j]
                        if 0 <= ex < mx and 0 <= ey < my:
                            if maze[ey][ex] == 1:
                                ctr += 1
                    if ctr == 1:
                        nlst.append(i)
        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            ir = nlst[np.random.randint(0, len(nlst))]
            cx += dx[ir]
            cy += dy[ir]
            stack.append((cx, cy))
        else:
            stack.pop()

    if check_maze(maze):
        correct_maze = np.array(maze, dtype=np.int32)
    else:
        print(maze)
        raise Exception('Generated an incorrect maze')

    return correct_maze


def gen_maze_data(n: int, mx: int, my: int) -> torch.Tensor:
    """Generate n mazes of size mx by my as a n x mx x my torch tensor.
    Persists the tensor to {root}/data/mazes folder.


    Args:
        n: The number of mazes to generate.
        mx: The length of a maze.
        my: The height of a maze

    Returns:
        The tensor of generated mazes
    """
    mazes = np.zeros([n, mx, my])
    for i in range(n):
        mazes[i] = gen_maze(mx, my)
        if (i + 1) % 100 == 0:
            print("Generated {}/{} mazes...".format(i + 1, n))
    unique_maze = np.unique(mazes, axis = 0)
    number_unique = len(unique_maze)
    # print("{}/{} are unique".format(number_unique, n))

    while number_unique != n:
        temp_maze = gen_maze_data(n - number_unique, mx, my)
        temp_unique = np.unique(temp_maze, axis = 0)
        unique_maze = np.concatenate((unique_maze, temp_unique), axis=0)
        unique_maze = np.unique(unique_maze, axis = 0)
        number_unique = len(unique_maze)

    mazes = torch.from_numpy(unique_maze)

    return mazes


def check_maze(maze: np.ndarray) -> bool:
    """Checks whether the input is a valid maze. Checks the following:
        * there are no islands (i.e. there are no loops).
        * all white pixels are connected.

    Args:
        maze:  The maze to be evaluated

    Returns:
        Whether the maze is valid or not.
    """

    # single connected-component
    mx, my = maze.shape
    stack = [(j, i) for i in range(mx) for j in range(my) if maze[i, j] == 1]
    if len(stack) == 0:
        return False
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]  # 4 directions to move in the maze
    while len(stack) > 0:
        (cx, cy) = stack[-1]
        nlst = []  # list of available neighbors
        for i in range(4):
            nx = cx + dx[i]
            ny = cy + dy[i]
            if 0 <= nx < mx and 0 <= ny < my:
                if maze[ny][nx] == 0:
                    # of occupied neighbors must be 1
                    ctr = 0
                    for j in range(4):
                        ex = nx + dx[j]
                        ey = ny + dy[j]
                        if 0 <= ex < mx and 0 <= ey < my:
                            if maze[ey][ex] == 1:
                                ctr += 1
                    if ctr == 1:
                        nlst.append(i)
        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            return False
        else:
            stack.pop()
    return base_check_maze(maze)


def save_grid(mazes: np.ndarray, path: str) -> None:
    """Save a sample of the first 25 mazes in the mini batch as a 5x5 grid of images. Used for visual inspection
    of the results.

    Args:
        mazes: An array of size batch_size x maze_length x maze_height
        path: The path to the file where the grid will be persisted.

    Todo:
        Make grid size and sample size dynamic.
    """
    fig = plt.figure(1, dpi=160)

    grid = ImageGrid(fig, 111, nrows_ncols=(5, 5), axes_pad=0.04, )
    for i in range(25):
        grid[i].imshow(mazes[i, :, :], cmap='gray')
        grid[i].axes.get_xaxis().set_visible(False)
        grid[i].axes.get_yaxis().set_visible(False)

    plt.savefig(path, dpi=160, bbox_inches='tight')


def draw(maze: np.ndarray) -> None:
    plt.imshow(maze, cmap='gray')
    plt.axis('image')
    plt.show(block=False)
    plt.pause(0.5)
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=str, default='generate', help='possible actions: generate, draw')
    parser.add_argument('-n', '--number', type=int, default=60000, help='number of mazes to generate')
    parser.add_argument('-s', '--size', type=int, default=8, help='the size of a maze, only square mazes are allowed')
    parser.add_argument('-p', '--path', type=str, default=None, help='where to save the images')
    opts = parser.parse_args()

    if opts.action == 'generate':
        print('Generating {} {}x{} mazes'.format(opts.number, opts.size, opts.size))
        data = gen_maze_data(opts.number, opts.size, opts.size)
        print("Training data contains only unique mazes now")
        print('Persisting data to file {}.{}x{}.data '.format(opts.number, opts.size, opts.size))
        path = os.path.join(ROOT, 'data', 'mazes', '{}.{}x{}.data.tar'.format(opts.number, opts.size, opts.size))
        torch.save(data, path)
    elif opts.action == 'draw':
        data = torch.load('../../data/mazes/{}.{}x{}.data.tar'.format(opts.number, opts.size, opts.size))
        os.makedirs(opts.path, exist_ok=True)
        save_grid(mazes=data, path='/'.join([opts.path, 'first_sample']))
    else:
        raise NotImplementedError('Unknown action: {}'.format(opts.action))
