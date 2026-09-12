import pytest
from simulator import one_node_sim


def test_one_milliamp_through_one_kilohm():
    voltage = one_node_sim(1000, 0.001)

    assert voltage == pytest.approx(1.0)

def test_10_milliamp_through_two_kilohm():
    voltage = one_node_sim(2000, 0.01)

    assert voltage == pytest.approx(20.0)

def test_0_milliamp_through_one_kiliohm():
    voltage = one_node_sim(1000, 0)

    assert voltage == pytest.approx(0.0)