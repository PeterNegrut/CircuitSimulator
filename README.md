# Circuit Simulator

A small SPICE-style circuit simulator built from scratch in Python, using
Modified Nodal Analysis (MNA) to solve linear circuits.

## Features

- Netlist parser for a simple, human-readable circuit description format
- DC analysis of resistors, independent voltage sources, and independent
  current sources
- Transient analysis of capacitors and inductors using the Backward Euler
  method, via companion (Norton-equivalent) models — no extra unknowns
  are added to the MNA system

## Supported components

| Prefix | Component         | Netlist line               |
|--------|--------------------|-----------------------------|
| `R`    | Resistor           | `R1 1 2 1000`               |
| `V`    | Voltage source     | `V1 1 0 10`                 |
| `I`    | Current source     | `I1 1 0 0.01`                |
| `C`    | Capacitor          | `C1 1 0 1e-6`                |
| `L`    | Inductor           | `L1 1 0 0.1`                 |

Each line has the form `<name> <node1> <node2> <value>`. Node `0` is
ground.

## Usage

```python
from simulator import parse_netlist, VoltageSource_Resistor_sim, backward_euler_sim

# DC analysis
netlist = """
V1 1 0 10
R1 1 2 1000
R2 2 0 2000
"""
components = parse_netlist(netlist)
node_voltages = VoltageSource_Resistor_sim(components)

# Transient analysis (RC charging through Backward Euler)
netlist = """
V1 1 0 10
R1 1 2 1000
C1 2 0 1e-6
"""
components = parse_netlist(netlist)
dt = 1e-6
steps = 1000
history = backward_euler_sim(components, dt, steps)
```

`backward_euler_sim` steps the circuit forward in time, updating each
capacitor's voltage and each inductor's current in place after every
step, and returns the list of node-voltage solutions, one per time step.

## Getting started

```bash
conda env create -f environment.yml
conda activate sim
python -c "import numpy, matplotlib, pytest; print('Environment ready')"
```

## Running the tests

```bash
pytest
```

## How it works

The simulator builds the system `Ax = b` from Modified Nodal Analysis:

- `A` is the conductance matrix, assembled by "stamping" each
  component's contribution onto the node equations.
- `x` is the vector of unknown node voltages (plus one unknown current
  per voltage source).
- `b` holds the known source terms.

Capacitors and inductors are discretized with the Backward Euler method,
which turns each into an equivalent resistor in parallel with a current
source that depends on the component's state from the previous time
step:

- **Capacitor**: conductance `C/dt` in parallel with a current source
  proportional to the previous step's voltage.
- **Inductor**: conductance `dt/L` in parallel with a current source
  equal to the previous step's current.

Because both companion models are expressed as a conductance plus a
current source, they stamp into the MNA system exactly like a resistor
and current source do, keeping the solver simple.

## Project status

- [x] DC analysis (resistors, voltage sources, current sources)
- [x] Backward Euler transient analysis (capacitors, inductors)
- [ ] Additional integration methods (e.g. Trapezoidal)
- [ ] Nonlinear components
