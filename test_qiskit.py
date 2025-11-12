from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# Create a Quantum Circuit with 1 quantum bit and 1 classical bit
qc = QuantumCircuit(1, 1)

# Add a 'Hadamard' gate on qubit 0
# This puts the qubit into a superposition (50% chance of 0, 50% chance of 1)
qc.h(0)

# Measure the qubit and store the result in the classical bit
qc.measure(0, 0)

# Create a simulator
simulator = AerSimulator()

# Compile the circuit for the simulator
compiled_circuit = transpile(qc, simulator)

# Run the circuit on the simulator 1000 times
job = simulator.run(compiled_circuit, shots=1000)

# Get the results
result = job.result()
counts = result.get_counts(qc)

# Print the results
print("\nTotal counts for 0 and 1 are:", counts)

# (Optional) Display the circuit diagram
print(qc.draw(output='text'))