import torch
import torch.nn as nn
from torch.distributions.relaxed_bernoulli import RelaxedBernoulli


class Discriminator:
    def __init__(self,
                 device,
                 hidden_size,
                 maze_size,
                 num_epochs,
                 batch_size,
                 writer):
        self.device = device
        self.hidden_size = hidden_size
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.model = nn.Sequential(
            nn.Linear(maze_size, hidden_size),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid())
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0002)
        self.writer = writer
        input = (torch.rand([batch_size - 1, maze_size]))
        # writer.add_graph(model=self.model, input_to_model=(input,), verbose=True)
        self.model = self.model.to(self.device)

    def train(self,
              G,
              input_size,
              mazes,
              loss_criterion,
              real_labels,
              fake_labels,
              reset_grad):
        # Loss starts (x, y): - y * log(D(x)) - (1-y) * log(1 - D(x))

        reset_grad()
        test_tensor = torch.tensor([0.75]).to(self.device)
        m = RelaxedBernoulli(test_tensor, probs=mazes)
        mazes = m.sample()
        outputs = self.model(mazes)
        d_loss_real = loss_criterion(outputs, real_labels)
        d_loss_real.backward()
        real_score = outputs

        ##Fake Data BCE_Loss
        # Generate fake data first
        z = torch.randn(self.batch_size, input_size).to(self.device)
        fake_mazes = G(z)
        test_tensor = torch.tensor([0.75]).to(self.device)
        m = RelaxedBernoulli(test_tensor, probs=fake_mazes)
        fake_mazes = m.sample()
        outputs = self.model(fake_mazes)
        # Fake data loss
        fake_score = outputs
        d_loss_fake = loss_criterion(outputs, fake_labels)
        d_loss_fake.backward()

        self.optimizer.step()

        return d_loss_fake + d_loss_real, fake_score, real_score, fake_mazes

    def backprop(self, d_loss_fake, d_loss_real, reset_grad):
        d_loss = d_loss_real + d_loss_fake
        reset_grad()
        d_loss.backward()
        self.optimizer.step()
        return d_loss