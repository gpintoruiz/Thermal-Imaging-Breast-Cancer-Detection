# PyTorch torchvision
from torchvision.transforms import v2

# Pytorch essentials
import torch
import torch.nn as nn

# wandb essentials
import wandb

# Make datasets
from make_dataset import get_data, make_loader

# Models
from xception import xception
from vgg import vgg
from alexnet import alexnet
from resnet56 import resnet56

# Pytorch metrics
from torchmetrics.classification import BinaryAccuracy, BinaryF1Score, BinaryRecall, BinaryPrecision

# Create plots
import matplotlib.pyplot as plt

# File management
import os
# from datetime import datetime

# Device configuration
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def make(config, fold=None):
    
    # Make transforms for data
    transform = make_transforms(augmentation=config.augmented)

    # Make the data
    train, test = get_data(transform=transform, slice=1, 
                                normalize=config.normalize, fold=fold, 
                                crop=config.crop)
    
    input_size = train[0][0].size()

    train_loader = make_loader(train, batch_size=config.batch_size)
    # val_loader = make_loader(val, batch_size=config.batch_size)
    test_loader = make_loader(test, batch_size=config.batch_size)

    # Make the model
    model = make_model(config.architecture, input_size).to(DEVICE)

    del input_size

    # Make the loss 
    criterion = nn.BCEWithLogitsLoss()
    # Gradient optimization algorithms. AFTER moving the model to the GPU.
    optimizer = build_optimizer(model, config.optimizer, config.learning_rate)

    # N-epochs to train
    epochs = config.epochs

    # Make metrics
    accuracy_fn = BinaryAccuracy().to(DEVICE)
    f1_score_fn = BinaryF1Score().to(DEVICE)
    recall_fn = BinaryRecall().to(DEVICE)
    precision_fn = BinaryPrecision().to(DEVICE)

    return model, train_loader, test_loader, criterion, optimizer, accuracy_fn, f1_score_fn, recall_fn, precision_fn, epochs

def make_transforms(augmentation=False):

  # https://pytorch.org/vision/main/transforms.html#performance-considerations
  transforms_list = [
    v2.ToImage(),
  ]

  if augmentation:
      # print("Efectivamente, voy a hacer transformaciones")
      transforms_list.append(v2.RandomHorizontalFlip())
      transforms_list.append(v2.RandomVerticalFlip())
      transforms_list.append(v2.RandomRotation(degrees=45)) # Aplica una rotación aleatoria de hasta 45 grados.
      transforms_list.append(v2.RandomApply([v2.GaussianBlur(kernel_size=5)], p=0.5)) # Aplica un desenfoque gaussiano con una probabilidad de 0.5.
      transforms_list.append(v2.RandomApply([v2.RandomAffine(degrees=0, translate=(0.05, 0.05))], p=0.5)) # Aplica pequeñas traslaciones (hasta el 5% del tamaño de la imagen).

  transform = v2.Compose(transforms_list)

  return transform

def build_optimizer(network, optimizer, learning_rate):
  if optimizer == "sgd":
      # print("Efectivamente, voy a usar SGD")
      optimizer = torch.optim.SGD(network.parameters(),
                            lr=learning_rate, momentum=0.9)
  elif optimizer == "adam":
      # print("Efectivamente, voy a usar Adam")
      optimizer = torch.optim.Adam(network.parameters(),
                              lr=learning_rate)
  return optimizer

def make_model(architecture:str, input_size:list=[1, 480, 640]):
  if architecture=='xception':
      model = xception(n_channels=1, n_classes=1)
  elif architecture=='vgg':
      model = vgg(num_classes=1, input_size=input_size)
  elif architecture=='alexnet':
      model = alexnet(num_classes=1, input_size=input_size)
    # pass
  elif architecture=='resnet56':
      model = resnet56(n=9,num_classes=1)
  return model

def visualize_batch_inference(images, ground_truths, predictions):
    batch_size = len(images)
    cols = 4  # Número de columnas para la cuadrícula
    rows = (batch_size + cols - 1) // cols  # Número de filas necesario

    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))

    for i in range(batch_size):
        row = i // cols
        col = i % cols
        ax = axes[row, col] if rows > 1 else axes[col]

        # Mostrar la imagen en escala de grises con colormap 'inferno'
        ax.imshow(images[i].squeeze(0), cmap='inferno')
        
        # Anotaciones para ground truth y predicción
        gt_text = f"True: {'Benign' if ground_truths[i] else 'Malignant'}"
        pred_text = f"Prediction: {'Benign' if predictions[i] else 'Malignant'}"
        ax.set_title(f'{gt_text} | {pred_text}')
        ax.axis('off')

    # Desactivar los ejes sobrantes
    for j in range(i + 1, rows * cols):
        row = j // cols
        col = j % cols
        ax = axes[row, col] if rows > 1 else axes[col]
        ax.axis('off')

    plt.tight_layout()
    # plt.show()

    return fig

def save_model(gkfold_path:str, checkpoint:dict):
  # Crear la carpeta models por si no existe
  if not os.path.exists('../models'):
    os.mkdir("../models")
  
  model_path = f'{gkfold_path}.pth'
  torch.save(checkpoint, model_path)

  artifact = wandb.Artifact('model', type='model')
  artifact.add_file(model_path)
  wandb.log_artifact(artifact)
  
