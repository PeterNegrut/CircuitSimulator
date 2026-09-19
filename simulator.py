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

        nodes.discard("0")

    return {
        node: index
        for index, node in enumerate(sorted(nodes))
    }

            




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
    R2 vout 0 2000
"""
    components = parse_netlist(netlist)
    print(components)
    node_map = build_node_map(components)
    print(node_map)
