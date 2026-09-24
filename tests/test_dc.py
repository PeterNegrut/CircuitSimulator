import pytest
from simulator import one_node_sim
from simulator import VoltageSource_Resistor_sim
from simulator import parse_netlist
from simulator import build_node_map


def test_one_milliamp_through_one_kilohm():
    voltage = one_node_sim(1000, 0.001)

    assert voltage == pytest.approx(1.0)

def test_10_milliamp_through_two_kilohm():
    voltage = one_node_sim(2000, 0.01)

    assert voltage == pytest.approx(20.0)

def test_0_milliamp_through_one_kiliohm():
    voltage = one_node_sim(1000, 0)

    assert voltage == pytest.approx(0.0)

def test_voltage_divider():
    netlist = """
        V1 1 0 10
        R1 1 2 1000
        R2 2 0 2000
    """
    components = parse_netlist(netlist)
    x = VoltageSource_Resistor_sim(components)
    assert x[0] == pytest.approx(10.0)
    assert x[1] == pytest.approx(6.666667)
    assert x[2] == pytest.approx(-10/3000)

def test_3_node():
    netlist = """
        V1 1 0 10
        R1 1 2 1000
        R2 2 0 2000
        R3 2 3 1000
        R4 3 0 2000
    """

    components = parse_netlist(netlist)
    x = VoltageSource_Resistor_sim(components)

    assert x[0] == pytest.approx(10.0)
    assert x[1] == pytest.approx(60 / 11)       # 5.4545 V
    assert x[2] == pytest.approx(40 / 11)       # 3.6364 V
    assert x[3] == pytest.approx(-50 / 11000)   # -4.545 mA

def test_current_source_to_ground():
    netlist = """
        I1 0 1 0.01
        R1 1 0 1000
    """

    components = parse_netlist(netlist)
    x = VoltageSource_Resistor_sim(components)

    assert x[0] == pytest.approx(10.0)

def test_voltage_and_current_source():
    netlist = """
        V1 1 0 10
        R1 1 2 1000
        R2 2 0 1000
        I1 2 0 0.002
    """

    components = parse_netlist(netlist)
    x = VoltageSource_Resistor_sim(components)

    assert x[0] == pytest.approx(10.0)      # V1
    assert x[1] == pytest.approx(4.0)       # V2
    assert x[2] == pytest.approx(-0.006)    # current through V1

def test_current_source_between_nodes():
    netlist = """
        I1 1 2 0.001
        R1 1 0 1000
        R2 2 0 2000
    """

    components = parse_netlist(netlist)
    x = VoltageSource_Resistor_sim(components)

    assert x[0] == pytest.approx(-1.0)   # V1
    assert x[1] == pytest.approx(2.0)    # V2