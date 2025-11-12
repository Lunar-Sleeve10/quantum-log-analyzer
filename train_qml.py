import numpy as np
from sklearn.preprocessing import MinMaxScaler
from qiskit_aer.primitives import Sampler as AerSampler
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_machine_learning.algorithms.classifiers import VQC
from qiskit_algorithms.utils import algorithm_globals
from qiskit_algorithms.optimizers import COBYLA
import joblib

print("Starting QML model training...")
algorithm_globals.random_seed = 42
NUM_FEATURES = 4 

def extract_features(log_entry):
    log_entry = log_entry.lower()
    length = len(log_entry)
    digits = sum(c.isdigit() for c in log_entry)
    keywords = log_entry.count('error') + log_entry.count('warn') + log_entry.count('failed')
    return [length, digits, keywords, 0.0]

normal_logs = [
    "[2024-11-12 10:00:00,INFO] User 'admin' successfully logged in.",
    "[2024-11-12 10:01:00,INFO] Service 'webserver' started.",
    "[2024-11-12 10:02:00,DEBUG] Cache cleared.",
]
anomaly_logs = [
    "[2024-11-12 10:01:00,WARN] Failed password for invalid user 'root' from 185.12.33.1",
    "[2024-11-12 10:02:00,ERROR] Database connection refused.",
    "[2024-11-12 10:03:00,WARN] Possible SQL injection attempt: ' OR 1=1",
]

X_normal = np.array([extract_features(log) for log in normal_logs])
X_anomaly = np.array([extract_features(log) for log in anomaly_logs])
X = np.concatenate((X_normal, X_anomaly))
y = np.array([0, 0, 0, 1, 1, 1])

scaler = MinMaxScaler().fit(X)
X_scaled = scaler.transform(X)

num_qubits = NUM_FEATURES
feature_map = ZZFeatureMap(feature_dimension=num_qubits, reps=1)
ansatz = RealAmplitudes(num_qubits=num_qubits, reps=3)
sampler = AerSampler()
optimizer = COBYLA(maxiter=100)

vqc = VQC(
    feature_map=feature_map,
    ansatz=ansatz,
    optimizer=optimizer,
    sampler=sampler,
)

vqc.fit(X_scaled, y)
print("Model training complete.")

vqc.save("qml_model.qml")
joblib.dump(scaler, 'scaler.pkl') 

print("Training complete! Models 'qml_model.qml' and 'scaler.pkl' saved.")