import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import warnings
warnings.filterwarnings('ignore')

class ThreatModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.feature_importance = {}
    
    def prepare_dataset(self, features: np.array, labels: np.array, test_size: float = 0.2):
        """Prepara el dataset para entrenamiento"""
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Entrena modelo Random Forest"""
        print("[+] Entrenando Random Forest...")
        
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        
        # Evaluación
        y_pred = rf_model.predict(X_test)
        y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': np.mean(y_pred == y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'feature_importance': dict(zip(
                [f'feature_{i}' for i in range(X_train.shape[1])],
                rf_model.feature_importances_
            ))
        }
        
        self.models['random_forest'] = {
            'model': rf_model,
            'metrics': metrics
        }
        
        return rf_model, metrics
    
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Entrena modelo XGBoost"""
        print("[+] Entrenando XGBoost...")
        
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        y_pred = xgb_model.predict(X_test)
        y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': np.mean(y_pred == y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        self.models['xgboost'] = {
            'model': xgb_model,
            'metrics': metrics
        }
        
        return xgb_model, metrics
    
    def train_anomaly_detector(self, X_train, contamination=0.1):
        """Entrena modelo de detección de anomalías"""
        print("[+] Entrenando detector de anomalías...")
        
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        
        iso_forest.fit(X_train)
        
        self.models['isolation_forest'] = {
            'model': iso_forest,
            'contamination': contamination
        }
        
        return iso_forest
    
    def train_ensemble(self, X_train, y_train, X_test, y_test):
        """Entrena modelo ensemble"""
        print("[+] Entrenando modelo ensemble...")
        
        from sklearn.ensemble import VotingClassifier
        
        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        xgb = xgb.XGBClassifier(random_state=42)
        
        ensemble = VotingClassifier(
            estimators=[('rf', rf), ('xgb', xgb)],
            voting='soft',
            n_jobs=-1
        )
        
        ensemble.fit(X_train, y_train)
        
        y_pred = ensemble.predict(X_test)
        y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': np.mean(y_pred == y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        self.models['ensemble'] = {
            'model': ensemble,
            'metrics': metrics
        }
        
        return ensemble, metrics
    
    def hyperparameter_tuning(self, X_train, y_train):
        """Búsqueda de mejores hiperparámetros"""
        from sklearn.model_selection import GridSearchCV
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10]
        }
        
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"[+] Mejores parámetros: {grid_search.best_params_}")
        print(f"[+] Mejor score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def compare_models(self):
        """Compara el performance de todos los modelos"""
        comparison = {}
        
        for name, model_data in self.models.items():
            if 'metrics' in model_data:
                comparison[name] = {
                    'accuracy': model_data['metrics']['accuracy'],
                    'roc_auc': model_data['metrics'].get('roc_auc', 0)
                }
        
        # Seleccionar el mejor modelo
        if comparison:
            best_model = max(comparison.items(), key=lambda x: x[1]['roc_auc'])
            self.best_model = best_model[0]
            print(f"[+] Mejor modelo: {best_model[0]} (AUC: {best_model[1]['roc_auc']:.4f})")
        
        return comparison