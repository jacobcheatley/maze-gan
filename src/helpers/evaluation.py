from helpers import maze_utils as mu
from helpers import misc
import torch


def check_ind(files):
    for file in files:
        correct = 0
        sample = torch.load(file).numpy()
        for maze in sample:
            correct += int(mu.check_maze(maze))
        print(file, correct, '/', sample.shape[0])


def check_avg(files):
    for idx, chunk in enumerate(misc.chunks(files, 100)):
        correct = 0
        total = 0
        for file in chunk:
            sample = torch.load(file).numpy()
            total += sample.shape[0]
            for maze in sample:
                correct += int(mu.check_maze(maze))

        print(idx, ':', correct, '/', total)


def check_and_draw(files):
    for file in files:
        correct = 0
        sample = torch.load(file).numpy()
        for maze in sample:
            check = mu.check_maze(maze)
            correct += int(check)
            if check:
                mu.draw(maze)
        if correct > 0:
            print(file, correct, '/', sample.shape[0])