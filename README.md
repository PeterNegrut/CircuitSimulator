Purpose: Learn how circuit equations become a working numerical simulator.
Planned first release: Linear DC circuits and RC transient simulation.
Current status: Project setup complete; circuit solving not implemented yet.
Next milestone: Solve the \(1\ \mathrm{mA}\), \(1\ \mathrm{k\Omega}\) example.

conda env create -f environment.yml
conda activate sim
python -c "import numpy, matplotlib, pytest; print('Environment ready')"

Simulator solves Ax=b: Base Case is a 1 mA direct current soruce in series with a 1 mOhm resistor thats grounded. The simulator solves Ax = b, A is the coefficient coming from 1/R set as a variable G (ohms, conductance); x is the unkown node voltage, and b is the known current source value. We solve 1/1000 (x) = 0.001 giving x = 1V.
