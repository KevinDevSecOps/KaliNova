import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import Dataset, DataLoader
import json

class Generator(nn.Module):
    """Generador para crear tráfico de red sintético"""
    def __init__(self, latent_dim=100, output_dim=50):
        super(Generator, self).__init__()
        self.latent_dim = latent_dim
        
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(128),
            nn.Linear(128, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            nn.Linear(512, output_dim),
            nn.Tanh()
        )
    
    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    """Discriminador para detectar tráfico malicioso"""
    def __init__(self, input_dim=50):
        super(Discriminator, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.model(x)

class GANThreatDetector:
    def __init__(self, feature_dim=50, latent_dim=100):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.generator = Generator(latent_dim, feature_dim).to(self.device)
        self.discriminator = Discriminator(feature_dim).to(self.device)
        
        self.optimizer_G = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.optimizer_D = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        self.criterion = nn.BCELoss()
        self.feature_dim = feature_dim
        
    def train(self, real_data, epochs=10000, batch_size=32):
        """Entrena la GAN"""
        real_data = torch.FloatTensor(real_data).to(self.device)
        
        for epoch in range(epochs):
            # Entrenar Discriminador
            self.optimizer_D.zero_grad()
            
            # Datos reales
            real_labels = torch.ones(batch_size, 1).to(self.device)
            real_output = self.discriminator(real_data[:batch_size])
            d_loss_real = self.criterion(real_output, real_labels)
            
            # Datos generados
            z = torch.randn(batch_size, self.generator.latent_dim).to(self.device)
            fake_data = self.generator(z)
            fake_labels = torch.zeros(batch_size, 1).to(self.device)
            fake_output = self.discriminator(fake_data.detach())
            d_loss_fake = self.criterion(fake_output, fake_labels)
            
            # Pérdida total del discriminador
            d_loss = d_loss_real + d_loss_fake
            d_loss.backward()
            self.optimizer_D.step()
            
            # Entrenar Generador
            self.optimizer_G.zero_grad()
            
            fake_output = self.discriminator(fake_data)
            g_loss = self.criterion(fake_output, real_labels)
            g_loss.backward()
            self.optimizer_G.step()
            
            if epoch % 1000 == 0:
                print(f'Epoch [{epoch}/{epochs}] - D_loss: {d_loss.item():.4f}, G_loss: {g_loss.item():.4f}')
    
    def detect_anomalies(self, network_data):
        """Detecta anomalías usando el discriminador entrenado"""
        with torch.no_grad():
            data_tensor = torch.FloatTensor(network_data).to(self.device)
            predictions = self.discriminator(data_tensor)
            
        return predictions.cpu().numpy()