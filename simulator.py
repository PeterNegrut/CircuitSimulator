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

netlist = """
    V1 1 0 10
    V2 1 2 1000
    R2 vout 0 2000
"""



def one_node_sim(resistance_ohms, current_amps):
    conductance = 1/resistance_ohms
    A = np.array([[conductance]])
    b = np.array([current_amps])
    x = np.linalg.solve(A, b)
    return float(x[0])


 
if __name__ == "__main__":
    components = parse_netlist(netlist)
    for component in components:
        print(component)
