import math

import pytest

from simulator import parse_netlist, backward_euler_sim


def test_capacitor_single_step_matches_companion_model():
    dt = 1e-6
    r = 1000.0
    c = 1e-6
    v_source = 10.0

    netlist = f"""
        V1 1 0 {v_source}
        R1 1 2 {r}
        C1 2 0 {c}
    """

    components = parse_netlist(netlist)
    [x] = backward_euler_sim(components, dt, steps=1)

    g_r = 1.0 / r
    g_c = c / dt
    expected_v2 = g_r * v_source / (g_r + g_c)

    assert x[1] == pytest.approx(expected_v2)
    assert components[2].voltage == pytest.approx(expected_v2)


def test_inductor_single_step_matches_companion_model():
    dt = 1e-6
    r = 1000.0
    l = 0.1
    v_source = 10.0

    netlist = f"""
        V1 1 0 {v_source}
        R1 1 2 {r}
        L1 2 0 {l}
    """

    components = parse_netlist(netlist)
    [x] = backward_euler_sim(components, dt, steps=1)

    g_r = 1.0 / r
    g_l = dt / l
    expected_v2 = g_r * v_source / (g_r + g_l)
    expected_current = g_l * expected_v2

    assert x[1] == pytest.approx(expected_v2)
    assert components[2].current == pytest.approx(expected_current)


def test_rc_charging_matches_analytic_curve():
    r = 1000.0
    c = 1e-6
    v_source = 10.0
    dt = 1e-6
    steps = 1000  # 1 ms = one RC time constant

    netlist = f"""
        V1 1 0 {v_source}
        R1 1 2 {r}
        C1 2 0 {c}
    """

    components = parse_netlist(netlist)
    results = backward_euler_sim(components, dt, steps)

    final_v2 = results[-1][1]
    tau = r * c
    expected = v_source * (1 - math.exp(-steps * dt / tau))

    assert final_v2 == pytest.approx(expected, rel=0.01)


def test_rl_current_rise_matches_analytic_curve():
    r = 1000.0
    l = 0.1
    v_source = 10.0
    dt = 1e-7
    steps = 1000  # 0.1 ms = one L/R time constant

    netlist = f"""
        V1 1 0 {v_source}
        R1 1 2 {r}
        L1 2 0 {l}
    """

    components = parse_netlist(netlist)
    backward_euler_sim(components, dt, steps)

    inductor = components[2]
    tau = l / r
    expected = (v_source / r) * (1 - math.exp(-steps * dt / tau))

    assert inductor.current == pytest.approx(expected, rel=0.01)


def test_dt_required_for_capacitor():
    from simulator import VoltageSource_Resistor_sim

    netlist = """
        V1 1 0 10
        R1 1 2 1000
        C1 2 0 1e-6
    """

    components = parse_netlist(netlist)

    with pytest.raises(ValueError):
        VoltageSource_Resistor_sim(components)
