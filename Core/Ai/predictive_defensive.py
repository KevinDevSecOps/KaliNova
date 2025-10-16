import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class PredictiveDefenseAgent:
    """Agente de RL para defensa predictiva de redes"""
    def __init__(self, state_size=50, action_size=10):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
    
    def _build_model(self):
        """Construye la red neuronal para Q-learning"""
        model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_size)
        ).to(self.device)
        return model
    
    def update_target_model(self):
        """Actualiza el modelo target"""
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        """Almacena experiencia en memoria"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """Selecciona acción usando política epsilon-greedy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_values = self.model(state)
        return np.argmax(q_values.cpu().data.numpy())
    
    def replay(self, batch_size=32):
        """Entrena el modelo con experiencias pasadas"""
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        states = torch.FloatTensor([e[0] for e in minibatch]).to(self.device)
        actions = torch.LongTensor([e[1] for e in minibatch]).to(self.device)
        rewards = torch.FloatTensor([e[2] for e in minibatch]).to(self.device)
        next_states = torch.FloatTensor([e[3] for e in minibatch]).to(self.device)
        dones = torch.BoolTensor([e[4] for e in minibatch]).to(self.device)
        
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        next_q = self.target_model(next_states).max(1)[0].detach()
        target_q = rewards + (self.gamma * next_q * ~dones)
        
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class PredictiveSecuritySystem:
    def __init__(self):
        self.defense_agent = PredictiveDefenseAgent()
        self.optimizer = optim.Adam(self.defense_agent.model.parameters(), 
                                  lr=self.defense_agent.learning_rate)
        self.defense_actions = [
            'block_ip_temporary', 'increase_monitoring', 'isolate_subnet',
            'deploy_honeypot', 'enable_ips', 'throttle_connections',
            'require_mfa', 'alert_soc', 'backup_critical_data', 'patch_system'
        ]
    
    async def analyze_and_respond(self, network_state):
        """Analiza el estado de la red y ejecuta acciones defensivas"""
        state_vector = self.extract_state_features(network_state)
        action = self.defense_agent.act(state_vector)
        
        # Ejecutar acción defensiva
        reward = await self.execute_defensive_action(action, network_state)
        
        # Observar nuevo estado
        new_state = self.observe_new_state()
        
        # Aprender de la experiencia
        self.defense_agent.remember(state_vector, action, reward, new_state, False)
        self.defense_agent.replay()
        
        return action, reward
    
    async def execute_defensive_action(self, action_idx, network_state):
        """Ejecuta una acción defensiva específica"""
        action = self.defense_actions[action_idx]
        print(f"   🛡️  Ejecutando acción defensiva: {action}")
        
        # Simular ejecución de acciones
        if action == 'block_ip_temporary':
            return await self.block_ip_temporary(network_state.get('suspicious_ip'))
        elif action == 'deploy_honeypot':
            return await self.deploy_targeted_honeypot(network_state)
        elif action == 'enable_ips':
            return await self.enable_intrusion_prevention()
        
        return 0.1  # Recompensa base
    
    async def block_ip_temporary(self, ip_address):
        """Bloquea IP temporalmente"""
        print(f"      🔒 Bloqueando IP {ip_address} por 30 minutos")
        return 0.5
    
    async def deploy_targeted_honeypot(self, network_state):
        """Despliega honeypot específico para la amenaza"""
        print("      🍯 Desplegando honeypot dirigido")
        return 0.7