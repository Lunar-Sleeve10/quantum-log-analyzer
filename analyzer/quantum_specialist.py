import numpy as np
import joblib
from qiskit_aer.primitives import Sampler as AerSampler
from qiskit_machine_learning.algorithms.classifiers import VQC
from qiskit_algorithms.utils import algorithm_globals
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'qml_model.qml')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

def extract_features(log_entry):
    log_entry = log_entry.lower()
    length = len(log_entry)
    digits = sum(c.isdigit() for c in log_entry)
    keywords = log_entry.count('error') + log_entry.count('warn') + log_entry.count('failed')
    return [length, digits, keywords, 0.0]

print("[Quantum Scan]: Loading pre-trained models...")
try:
    scaler = joblib.load(SCALER_PATH)
    loaded_vqc = VQC.load(MODEL_PATH)
    
    loaded_vqc.sampler = AerSampler()
    print("[Quantum Scan]: Models loaded successfully.")
except FileNotFoundError:
    print(f"[Quantum Scan]: ERROR! Model files not found at expected paths: {MODEL_PATH} or {SCALER_PATH}. Run 'python train_qml.py' first.")
    scaler, loaded_vqc = None, None
except Exception as e:
    print(f"[Quantum Scan]: An unexpected error occurred loading models: {e}")
    scaler, loaded_vqc = None, None

def run_quantum_scan(log_entry_data):
    if not all([loaded_vqc, scaler]):
        return "ERROR: QML MODEL NOT LOADED."

    try:
        features = np.array([extract_features(log_entry_data)])
        features_scaled = scaler.transform(features)
        prediction_raw = loaded_vqc.predict(features_scaled)
        
        if np.ndim(prediction_raw) == 0:
            prediction = int(np.round(prediction_raw))
        else:
            prediction = int(np.round(prediction_raw[0]))
        
        if prediction == 1:
            return "ANOMALY DETECTED (Real QML)"
        else:
            return "No Anomaly (Real QML)"
    
    except Exception as e:
        print(f"[Quantum Scan]: ERROR during prediction: {e}")
        return "ERROR: Prediction Failed"