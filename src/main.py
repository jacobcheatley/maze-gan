import argparse
import os
import torch
import pickle
from helpers.MazeGenerator import check_maze, draw_maze

from models.continuous.GeneralAdversarialNetwork import GeneralAdversarialNetwork

def_dir = 'maze_results'


def visualise_results(dir, eg_no):
    # path = os.path.join(dir, 'real_mazes.pickle')
    path = os.path.join(dir, 'fake_mazes-{}.pickle'.format(eg_no))
    print('Visualising sample from {}'.format(path))
    # visualise sample from final results
    mazes = pickle.load(open(path, 'rb'))
    # print(mazes)
    # takes sample and plot
    for maze in mazes[:10]:
        print(maze)
        maze[maze < 0.5] = 0
        maze[maze > 0.5] = 1
        # is it a valid maze?
        if torch.cuda.is_available(): maze = maze.cpu()
        maze = maze.detach().numpy()
        check = check_maze(maze)
        if check:
            print(check)
            draw_maze(maze)
        else:
            print(check)
            draw_maze(maze)
    correct = 0
    for maze in mazes:
        maze[maze < 0.5] = 0
        maze[maze > 0.5] = 1
        if torch.cuda.is_available(): maze = maze.cpu()
        maze = maze.detach().numpy()
        check = check_maze(maze)
        if check:
            correct += 1
            draw_maze(maze)
    print(correct, ' correct out of ', len(mazes))


def test_results(dir, eg_no):
    path = os.path.join(dir, 'fake_mazes-{}.pickle'.format(eg_no))
    print('Testing results from {}'.format(path))
    mazes = pickle.load(open(path, 'rb'))
    # print(mazes)
    r = []
    for each_maze in mazes:
        r.append(check_maze(each_maze))
    print(len(r))


def start():
    # look for cmd arguments here

    parser = argparse.ArgumentParser(description='Run GAN or visualise maze.')
    parser.add_argument('--v', '--visualise', action='store', nargs=2, help='Visualise a sample of fake results')
    parser.add_argument('--t', '--test', action='store', nargs=2, help='Test fake results')
    # ------ Have to check which are rows and columns -------#
    parser.add_argument('--mx', help='No. columns in maze', type=int, default=28)
    parser.add_argument('--my', help='No. rows in maze', type=int, default=28)
    parser.add_argument('--N', help='No. of training examples to generate', type=int, default=1000)
    # -------------------------------------------------------#
    parser.add_argument('--latent_size', help='No. inputs for generator', type=int, default=64)
    parser.add_argument('--hidden_size', help='No. of hidden neurons', type=int, default=256)
    parser.add_argument('--num_epochs', help='No. of epochs', type=int,
                        default=200)
    parser.add_argument('--batch_size', help='Size of batch to use (Must be compatible with N)', type=int, default=100)

    parser.add_argument('--g_lr', help='Generator learning rate', type=float, default=0.0002)
    parser.add_argument('--d_lr', help='Discriminator learning rate', type=float, default=0.0002)

    parser.add_argument('--model', help='Which model to train', type=str, default='mnist')
    parser.add_argument('--resume', help='Whether to resume or start fresh', type=bool, default=False)

    args = parser.parse_args()

    if args.v:
        visualise_results(args.v[0], args.v[1])
    elif args.t:
        test_results(args.t[0], args.t[1])
    else:
        if args.model == 'mnist':
            gan = GeneralAdversarialNetwork(args)
            gan.train()
        elif args.model == 'maze':
            raise NotImplementedError


if __name__ == '__main__':
    start()
