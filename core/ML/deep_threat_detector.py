import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

class ThreatDataset(Dataset):
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

class ThreatNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_layers=[128, 64, 32], num_classes=2):
        super(ThreatNeuralNetwork, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_layers:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.3))
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, num_classes))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

class DeepThreatDetector:
    def __init__(self, input_size, learning_rate=0.001):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ThreatNeuralNetwork(input_size).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Entrena la red neuronal"""
        train_dataset = ThreatDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        val_dataset = ThreatDataset(X_val, y_val)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        train_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            total_loss = 0
            
            for batch_features, batch_labels in train_loader:
                batch_features, batch_labels = batch_features.to(self.device), batch_labels.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_features)
                loss = self.criterion(outputs, batch_labels)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            # Validation
            self.model.eval()
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_features, batch_labels in val_loader:
                    batch_features, batch_labels = batch_features.to(self.device), batch_labels.to(self.device)
                    outputs = self.model(batch_features)
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_labels.size(0)
                    correct += (predicted == batch_labels).sum().item()
            
            accuracy = 100 * correct / total
            avg_loss = total_loss / len(train_loader)
            
            train_losses.append(avg_loss)
            val_accuracies.append(accuracy)
            
            if epoch % 10 == 0:
                print(f'Epoch [{epoch}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')
        
        return train_losses, val_accuracies
    
    def predict(self, X):
        """Realiza predicciones"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            outputs = self.model(X_tensor)
            _, predicted = torch.max(outputs.data, 1)
            return predicted.cpu().numpy()
    
    def save_model(self, path):
        """Guarda el modelo entrenado"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
    
    def load_model(self, path):
        """Carga un modelo pre-entrenado"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])