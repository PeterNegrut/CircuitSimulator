import numpy as np

from dataclasses import dataclass

@dataclass
class Resistor:
    name: str
    node1: str
    node2: str
    resistance: float

@dataclass
class VoltageSource:
    name: str
    positive: str
    negative: str
    voltage: float

@dataclass
class CurrentSource:
    name: str
    positive: str
    negative: str
    current: float

@dataclass
class Capacitor:
    name: str
    node1: str
    node2: str
    capacitance: float
    voltage: float = 0.0  # voltage (node1 - node2) from the previous time step

@dataclass
class Inductor:
    name: str
    node1: str
    node2: str
    inductance: float
    current: float = 0.0  # current (node1 -> node2) from the previous time step

def parse_netlist(text):
    components = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) != 4:
            raise ValueError(
                f"Line {line_number}: expected 4 fields, got {len(parts)}"
            )

        name, node1, node2, value_text = parts

        try:
            value = float(value_text)
        except ValueError:
            raise ValueError(
                f"Line {line_number}: invalid value {value_text!r}"
            )

        component_type = name[0].upper()

        if component_type == "R":
            components.append(
                Resistor(name, node1, node2, value)
            )

        elif component_type == "V":
            components.append(
                VoltageSource(name, node1, node2, value)
            )

        elif component_type == "I":
            components.append(
                CurrentSource(name, node1, node2, value)
            )
        elif component_type == "C":
            components.append(
                Capacitor(name, node1, node2, value)
            )
        elif component_type == "L":
            components.append(
                Inductor(name, node1, node2, value)
            )
        else:
            raise ValueError(
                f"Line {line_number}: unknown component {name!r}"
            )

    return components

def build_node_map(components):
    nodes = set()
    for component in components:
        if isinstance(component, Resistor):
            nodes.add(component.node1)
            nodes.add(component.node2)

        elif isinstance(component, VoltageSource):
            nodes.add(component.positive)
            nodes.add(component.negative)

        elif isinstance(component, CurrentSource):
            nodes.add(component.positive)
            nodes.add(component.negative)

        elif isinstance(component, (Capacitor, Inductor)):
            nodes.add(component.node1)
            nodes.add(component.node2)

        nodes.discard("0")

    return {
        node: index
        for index, node in enumerate(sorted(nodes))
    }

def _stamp_conductance(A, node_map, node1, node2, conductance):
    if node1 != "0":
        i = node_map[node1]
        A[i, i] += conductance

    if node2 != "0":
        j = node_map[node2]
        A[j, j] += conductance

    if node1 != "0" and node2 != "0":
        i = node_map[node1]
        j = node_map[node2]

        A[i, j] -= conductance
        A[j, i] -= conductance

def _stamp_current_source(b, node_map, positive, negative, current):
    if positive != "0":
        b[node_map[positive]] -= current

    if negative != "0":
        b[node_map[negative]] += current

def VoltageSource_Resistor_sim(components, dt=None):

    node_map = build_node_map(components)

    num_nodes = len(node_map)

    num_voltage_sources = sum(
        isinstance(component, VoltageSource)
        for component in components
    )

    has_dynamic_component = any(
        isinstance(component, (Capacitor, Inductor))
        for component in components
    )

    if has_dynamic_component and dt is None:
        raise ValueError(
            "dt must be provided to simulate capacitors or inductors"
        )

    matrix_size = num_nodes + num_voltage_sources

    A = np.zeros((matrix_size, matrix_size))
    b = np.zeros(matrix_size)

    for component in components:

        if isinstance(component, Resistor):

            g = 1.0 / component.resistance
            _stamp_conductance(A, node_map, component.node1, component.node2, g)

        elif isinstance(component, Capacitor):

            # Backward Euler companion model: a conductance C/dt in
            # parallel with a current source that carries the previous
            # time step's voltage forward.
            g = component.capacitance / dt
            _stamp_conductance(A, node_map, component.node1, component.node2, g)

        elif isinstance(component, Inductor):

            # Backward Euler companion model: a conductance dt/L in
            # parallel with a current source that carries the previous
            # time step's current forward.
            g = dt / component.inductance
            _stamp_conductance(A, node_map, component.node1, component.node2, g)

    for component in components:

        if isinstance(component, Capacitor):

            g = component.capacitance / dt
            history_current = g * component.voltage
            _stamp_current_source(
                b, node_map, component.node2, component.node1, history_current
            )

        elif isinstance(component, Inductor):

            _stamp_current_source(
                b, node_map, component.node1, component.node2, component.current
            )

    voltage_source_number = 0

    for component in components:

        if isinstance(component, VoltageSource):

            k = num_nodes + voltage_source_number
            voltage_source_number += 1

            if component.positive != "0":
                p = node_map[component.positive]

                A[p, k] += 1
                A[k, p] += 1

            if component.negative != "0":
                n = node_map[component.negative]

                A[n, k] -= 1
                A[k, n] -= 1

            b[k] += component.voltage

    for component in components:

        if isinstance(component, CurrentSource):

            if component.positive != "0":
                p = node_map[component.positive]
                b[p] -= component.current

            if component.negative != "0":
                n = node_map[component.negative]
                b[n] += component.current

    print("A:")
    print(A)

    print("b:")
    print(b)
    x = np.linalg.solve(A, b)
    return [float(value) for value in x]

def backward_euler_sim(components, dt, steps):
    node_map = build_node_map(components)
    results = []

    for _ in range(steps):
        x = VoltageSource_Resistor_sim(components, dt)

        for component in components:

            if isinstance(component, Capacitor):
                v1 = x[node_map[component.node1]] if component.node1 != "0" else 0.0
                v2 = x[node_map[component.node2]] if component.node2 != "0" else 0.0
                component.voltage = v1 - v2

            elif isinstance(component, Inductor):
                v1 = x[node_map[component.node1]] if component.node1 != "0" else 0.0
                v2 = x[node_map[component.node2]] if component.node2 != "0" else 0.0
                g = dt / component.inductance
                component.current += g * (v1 - v2)

        results.append(x)

    return results

def one_node_sim(resistance_ohms, current_amps):
    conductance = 1/resistance_ohms
    A = np.array([[conductance]])
    b = np.array([current_amps])
    x = np.linalg.solve(A, b)
    return float(x[0])


 
if __name__ == "__main__":

    netlist = """
    V1 1 0 10
    R1 1 2 1000
    I1 2 0 0.01
    R2 2 3 2000
"""
    components = parse_netlist(netlist)
    print(components)
    x= VoltageSource_Resistor_sim(components)
    print("x: ")
    print(x)
