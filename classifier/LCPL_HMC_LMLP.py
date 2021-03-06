import torch
import torch.nn.functional as F
from torch import nn, optim

from classifier import EachLevelClassifier


class LCPL_HMC_LMLP(EachLevelClassifier):

    def __init__(self, input_size, previous_number_of_class, hidden_size, number_of_class, use_dropout=True, learning_rate=0.001):
        self.hidden_size = hidden_size
        self.previous_number_of_class = previous_number_of_class
        super(LCPL_HMC_LMLP, self).__init__(input_size,
                                            number_of_class, use_dropout, learning_rate)

    def initial_structure(self):
        self.dense = nn.Linear(self.input_size +
                               self.previous_number_of_class, self.hidden_size)
        if self.use_dropout:
            self.dropout_input = nn.Dropout(p=0.15)
            self.dropout_prev = nn.Dropout(p=0.15)
            self.dropout = nn.Dropout(p=0.25)
        self.logit = nn.Linear(self.hidden_size, self.number_of_class)

    def forward(self, x):
        start_target = x.size()[1] - self.previous_number_of_class
        prev = x[:, start_target:]
        real_x = x[:, :start_target]
        if self.use_dropout:
            prev = self.dropout_prev(prev)
            real_x = self.dropout_input(real_x)
        x = torch.cat([prev, real_x], 1)
        x = F.relu(self.dense(x))
        if self.use_dropout:
            x = self.dropout(x)
        x = self.logit(x)
        return x
