# wandb essentials
import argparse
from types import SimpleNamespace
import wandb

# Utils
from utils import make
# from test import test
from train import train

default_config = SimpleNamespace(
    epochs=50,
    classes=1,
    n_channels=1,
    batch_size=8,
    learning_rate=0.00001,
    crop=True,
    normalize=True,
    augmented=False,
    # resize=100,
    optimizer='adam',
    dataset="ThermalBreastCancer",
    architecture="vgg")

def parse_args():
    "Override default argments"
    argparser = argparse.ArgumentParser(description="Process hyper-parameters")
    argparser.add_argument('--batch_size', type=int, default=default_config.batch_size, help="batch size")
    argparser.add_argument('--learning_rate', type=float, default=default_config.learning_rate, help="learning rate")
    argparser.add_argument('--optimizer', type=str, default=default_config.optimizer, help="optimizer")
    argparser.add_argument('--normalize', type=bool, default=default_config.normalize, help="normalize")
    # argparser.add_argument('--resize', type=bool, default=default_config.resize, help="resize")
    argparser.add_argument('--augmented', type=bool, default=default_config.augmented, help="augmented")
    argparser.add_argument('--architecture', type=str, default=default_config.architecture, help="architecture")
    argparser.add_argument('--crop', type=bool, default=default_config.crop, help="crop")
    args = argparser.parse_args()
    vars(default_config).update(vars(args))
    return

def model_pipeline(hyperparameters):

    # tell wandb to get started
    with wandb.init(project="dip-project", config=hyperparameters):
        # access all HPs through wandb.config, so logging matches execution!
        config = wandb.config

        # make the model, data, loss, metrics and optimization problem
        model, train_loader, test_loader, criterion, optimizer, accuracy_fn, f1_score_fn, recall_fn, precision_fn, epochs = make(config=config)
        # print(model)

        # and use them to train the model
        train(model, train_loader, test_loader, criterion, optimizer, accuracy_fn, f1_score_fn, recall_fn, precision_fn, epochs)

    return model


if __name__ == "__main__":
    parse_args()
    model_pipeline(default_config)