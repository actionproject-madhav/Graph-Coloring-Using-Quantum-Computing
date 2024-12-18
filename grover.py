from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Input parameters
NUMBER_OF_NODES = 4
EDGE_CONNECTIONS = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
SHOTS = 1024

# Qubit assignments
NODE_QUBITS_1D = list(range(NUMBER_OF_NODES * 2))
NODE_QUBITS_2D = [NODE_QUBITS_1D[i:i + 2] for i in range(0, len(NODE_QUBITS_1D), 2)]
EDGE_QUBITS = list(range(NUMBER_OF_NODES * 2, NUMBER_OF_NODES * 2 + len(EDGE_CONNECTIONS)))
ANCILLA_QUBIT = [NUMBER_OF_NODES * 2 + len(EDGE_CONNECTIONS)]
ALL_QUBITS = NODE_QUBITS_1D + EDGE_QUBITS + ANCILLA_QUBIT

# Debug output
print(f"Number of nodes: {NUMBER_OF_NODES}")
print(f"Edge connections: {EDGE_CONNECTIONS}")
print(f"Node qubits (1D): {NODE_QUBITS_1D}")
print(f"Edge qubits: {EDGE_QUBITS}")
print(f"Ancilla qubit: {ANCILLA_QUBIT}")
print(f"All qubits: {ALL_QUBITS}")

# Initialize quantum circuit
qc = QuantumCircuit(len(ALL_QUBITS), NUMBER_OF_NODES * 2)


def apply_initialization(qr):
    """Initialize qubits with Hadamard gates."""
    qc.h(qr)
    qc.barrier()


def apply_color_check(q0, q1, q2, q3, e):
    """Perform a color check on specified qubits."""
    qc.x([q2, q3])
    qc.mct([q0, q1], e)  # Multi-control Toffoli
    qc.mct([q1, q2], e)
    qc.mct([q2, q3], e)
    qc.mct([q0, q3], e)
    qc.x([q2, q3])
    qc.barrier()


def apply_oracle(edge_connections, ancilla):
    """Oracle to check color conflicts based on edge connections."""
    qc.barrier()
    for edge_idx, edge in enumerate(edge_connections):
        qubits = NODE_QUBITS_2D[edge[0]] + NODE_QUBITS_2D[edge[1]]
        apply_color_check(*qubits, EDGE_QUBITS[edge_idx])

    qc.mct(EDGE_QUBITS, ancilla[0])  # Multi-control Toffoli on all edges
    qc.barrier()


def prepare_state():
    """Prepare the initial state for Grover's algorithm."""
    apply_initialization(NODE_QUBITS_1D)
    qc.x(EDGE_QUBITS)
    qc.x(ANCILLA_QUBIT[0])
    qc.h(ANCILLA_QUBIT[0])


def apply_diffusion_operator():
    """Apply Grover's diffusion operator."""
    qc.h(NODE_QUBITS_1D)
    qc.x(NODE_QUBITS_1D)
    qc.h([NODE_QUBITS_1D[0]])  # Use one qubit as the control for diffusion
    qc.mct(NODE_QUBITS_1D[1:], NODE_QUBITS_1D[0])  # Multi-control Z-gate
    qc.h([NODE_QUBITS_1D[0]])
    qc.x(NODE_QUBITS_1D)
    qc.h(NODE_QUBITS_1D)
    qc.barrier()


def apply_grovers(number_of_iterations):
    """Apply Grover's algorithm."""
    prepare_state()
    for _ in range(number_of_iterations):
        apply_oracle(EDGE_CONNECTIONS, ANCILLA_QUBIT)
        apply_diffusion_operator()
    qc.measure(NODE_QUBITS_1D, range(NUMBER_OF_NODES * 2))  # Measure node qubits


def check_valid_coloring(binary_string):
    """Check if the coloring represented by binary_string is valid."""
    colors = [binary_string[i:i + 2] for i in range(0, len(binary_string), 2)]
    for edge in EDGE_CONNECTIONS:
        if colors[edge[0]] == colors[edge[1]]:
            return False
    return True


def draw_graph(binary_string):
    """Visualize the graph coloring."""
    color_map = {'00': 'red', '11': 'yellow', '01': 'blue', '10': 'green'}
    colors = [color_map[binary_string[i:i + 2]] for i in range(0, len(binary_string), 2)]

    G = nx.Graph()
    G.add_nodes_from(range(NUMBER_OF_NODES))
    G.add_edges_from(EDGE_CONNECTIONS)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2000)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)

    plt.axis('off')
    plt.show()


# Grover's algorithm loop
backend = Aer.get_backend('qasm_simulator')
iteration = 1

while True:
    qc = QuantumCircuit(len(ALL_QUBITS), NUMBER_OF_NODES * 2)
    apply_grovers(int(np.sqrt(4 ** NUMBER_OF_NODES) * iteration))

    # Execute simulation
    result = execute(qc, backend=backend, shots=SHOTS).result()
    counts = result.get_counts()
    print(f"Iteration {iteration}: Measurement results -> {counts}")

    # Take the most probable outcome
    binary_string = max(counts, key=counts.get)
    print(f"Proposed solution: {binary_string}")

    if check_valid_coloring(binary_string):
        print("Valid solution found!")
        draw_graph(binary_string)
        break
    iteration += 1
