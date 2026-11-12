from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dat_handler import AirfoilCoordinates, DATFormat, DATImporter, normalize_coordinates, scale_coordinates
from blade_root_geometry import BladeRootGeometry
from blade_root_materials import CompositeLaminate, MaterialDatabase
from structural_analysis import FatigueEngine, StructuralMaterial
from blade_model_library import PRESETS, blade_station_geometry, generate_blade
from turbulence_analysis import TurbulenceAnalyzer
from compare_reference_data import compare


def symmetric_airfoil() -> AirfoilCoordinates:
    x = np.array([1.0, 0.75, 0.5, 0.25, 0.0, 0.25, 0.5, 0.75, 1.0])
    y = np.array([0.0, 0.04, 0.06, 0.05, 0.0, -0.05, -0.06, -0.04, 0.0])
    return AirfoilCoordinates("symmetric-test", x, y, DATFormat.XFOIL)


def test_airfoil_normalization_hits_requested_chord_and_finite_coordinates():
    source = symmetric_airfoil()
    normalized = normalize_coordinates(source, target_chord=2.5)
    assert normalized.chord() == pytest.approx(2.5)
    assert np.all(np.isfinite(normalized.x))
    assert np.all(np.isfinite(normalized.y))
    assert normalized.max_thickness()[0] > 0.0


def test_airfoil_scaling_preserves_normalized_thickness_ratio():
    source = symmetric_airfoil()
    scaled = scale_coordinates(source, target_chord=3.0, center_leading_edge=False)
    assert scaled.chord() == pytest.approx(3.0)
    assert scaled.max_thickness()[0] == pytest.approx(source.max_thickness()[0], rel=1e-8)


def test_dat_importer_rejects_degenerate_geometry():
    content = "degenerate\n0 0\n0 0\n0 0\n"
    assert DATImporter._parse_content(content, "degenerate.dat") is None


def test_dovetail_geometry_has_positive_area_and_symmetry():
    profile = BladeRootGeometry().create_dovetail_profile(width=0.4, height=0.1, angle=45.0)
    assert np.isfinite(profile.area) and profile.area > 0.0
    assert profile.moment_inertia_xx > 0.0
    assert profile.moment_inertia_yy > 0.0
    assert profile.centroid[0] == pytest.approx(0.0, abs=1e-10)


def test_bolt_safety_factor_uses_strength_capacity_not_stiffness():
    geometry = BladeRootGeometry()
    kwargs = dict(
        bolt_diameter=0.02,
        bolt_circle_diameter=0.12,
        preload_percent=0.7,
        thread_pitch=0.002,
        clamp_length=0.04,
        yield_strength=640e6,
        applied_load=10_000.0,
    )
    one = geometry.compute_bolt_connection(bolt_count=1, **kwargs)
    two = geometry.compute_bolt_connection(bolt_count=2, **kwargs)
    tensile_area = np.pi * ((kwargs["bolt_diameter"] - 0.9382 * kwargs["thread_pitch"]) / 2.0) ** 2
    expected = tensile_area * kwargs["yield_strength"] * (1.0 - kwargs["preload_percent"]) / kwargs["applied_load"]
    assert one.safety_factor == pytest.approx(expected)
    assert two.safety_factor == pytest.approx(2.0 * expected)
    assert np.isfinite(one.stiffness) and one.stiffness > 0.0


def test_bolt_joint_rejects_nonphysical_dimensions():
    with pytest.raises(ValueError):
        BladeRootGeometry().compute_bolt_connection(
            bolt_count=4, bolt_diameter=0.02, bolt_circle_diameter=0.1,
            thread_pitch=0.03,
        )


def test_default_material_database_contains_physical_properties():
    database = MaterialDatabase()
    names = database.get_material_names()
    assert names
    for name in names:
        material = database.get_material(name)
        assert material is not None
        for attribute in ("density", "young_modulus", "yield_strength", "ultimate_strength"):
            value = getattr(material, attribute)
            assert np.isfinite(value) and value > 0.0


def test_structural_fatigue_turning_points_remove_plateaus_and_keep_extrema():
    values = np.array([0.0, 0.0, 2.0, 2.0, -1.0, -1.0, 3.0, 3.0])
    points = FatigueEngine.turning_points(values)
    assert points.tolist() == [0.0, 2.0, -1.0, 3.0]
    assert points[0] == values[0]
    assert points[-1] == values[-1]


def test_goodman_correction_increases_amplitude_for_positive_mean_stress():
    material = StructuralMaterial(
        name="test steel", young_modulus=200e9, poisson_ratio=0.3,
        density=7850.0, yield_strength=350e6, ultimate_strength=600e6,
        endurance_strength=200e6,
    )
    raw = FatigueEngine.corrected_amplitude(50e6, 0.0, material, "Goodman")
    corrected = FatigueEngine.corrected_amplitude(50e6, 100e6, material, "Goodman")
    assert raw == pytest.approx(50e6)
    assert corrected > raw
    assert np.isfinite(FatigueEngine.sn_life(50e6, 0.0, material, "Goodman"))


def test_fatigue_rainflow_handles_constant_signal_without_invalid_values():
    material = StructuralMaterial(
        name="test steel", young_modulus=200e9, poisson_ratio=0.3,
        density=7850.0, yield_strength=350e6, ultimate_strength=600e6,
        endurance_strength=200e6,
    )
    summary = FatigueEngine.evaluate(
        stress_history=np.full(20, 10e6),
        time=np.linspace(0.0, 1.0, 20),
        material=material,
    )
    assert np.isfinite(summary.damage)
    assert summary.damage >= 0.0


def test_symmetric_laminate_has_zero_coupling_and_correct_bending_rigidity():
    database = MaterialDatabase()
    material_name = database.get_material_names()[0]
    laminate = CompositeLaminate(database)
    thickness = 0.001
    ply = laminate.create_ply(material_name, 0.0, thickness)
    q_bar = laminate._transform_stiffness(ply)
    result = laminate.create_symmetric_layup(material_name, [0.0], thickness)
    total_thickness = 2.0 * thickness
    expected_d = q_bar * total_thickness**3 / 12.0
    assert np.allclose(result.B_matrix, np.zeros((3, 3)), rtol=1e-8, atol=1e-8)
    assert np.allclose(result.D_matrix, expected_d, rtol=1e-6, atol=1e-12)


def test_blade_station_geometry_matches_preset_endpoints():
    preset = PRESETS[0]
    chord, twist = blade_station_geometry(preset, [0.0, 0.5, 1.0])
    assert chord[0] == pytest.approx(preset.root_chord)
    assert chord[-1] == pytest.approx(preset.tip_chord)
    assert twist[0] == pytest.approx(preset.twist_root)
    assert twist[-1] == pytest.approx(preset.twist_tip)
    assert np.all(chord > 0.0)


def test_generated_blade_mesh_has_finite_points_and_expected_span():
    preset = PRESETS[0]
    mesh = generate_blade(preset, span_samples=8, airfoil_samples=24)
    assert mesh.n_points > 0 and mesh.n_cells > 0
    assert np.all(np.isfinite(mesh.points))
    assert mesh.bounds[5] - mesh.bounds[4] == pytest.approx(preset.length, rel=1e-6)


def test_turbulence_reynolds_number_matches_definition():
    analyzer = TurbulenceAnalyzer()
    value = analyzer.calculate_reynolds(velocity=10.0, density=1.2, viscosity=1.8e-5, length_scale=0.5)
    assert value == pytest.approx(1.2 * 10.0 * 0.5 / 1.8e-5)


def test_k_epsilon_turbulence_outputs_are_finite_and_nonnegative():
    result = TurbulenceAnalyzer().k_epsilon_model(reynolds=1e6, velocity=10.0, length_scale=0.5)
    assert all(np.isfinite(value) and value >= 0.0 for value in result.values())
    assert result["turbulent_kinetic_energy"] > 0.0
    assert result["dissipation_rate"] > 0.0


def test_mixed_material_laminate_uses_thickness_weighted_density():
    database = MaterialDatabase()
    laminate = CompositeLaminate(database)
    steel = laminate.create_ply("Steel_AISI_1040", 0.0, 0.001)
    aluminum = laminate.create_ply("Aluminum_6061_T6", 90.0, 0.003)
    result = laminate.analyze_laminate([steel, aluminum])
    expected_density = (7850.0 * 0.001 + 2700.0 * 0.003) / 0.004
    assert result.effective_density == pytest.approx(expected_density)
    assert result.failure_index is None
    assert result.failure_assessed is False
    assert result.is_safe is False


def test_laminate_rejects_empty_or_nonpositive_plies():
    laminate = CompositeLaminate(MaterialDatabase())
    with pytest.raises(ValueError):
        laminate.analyze_laminate([])
    with pytest.raises(ValueError):
        laminate.create_ply("Steel_AISI_1040", 0.0, 0.0)


def test_thermal_safety_factor_uses_stress_magnitude():
    from blade_root_materials import ThermalAnalyzer
    analyzer = ThermalAnalyzer(MaterialDatabase())
    result = analyzer.analyze_thermal_effects("Steel_AISI_1040", 293.0, -100e6, {})
    assert result.safety_factor == pytest.approx(350e6 / 100e6)


@pytest.mark.parametrize("kwargs", [
    dict(velocity=10.0, density=1.2, viscosity=0.0, length_scale=1.0),
    dict(velocity=-1.0, density=1.2, viscosity=1.8e-5, length_scale=1.0),
    dict(velocity=10.0, density=float("nan"), viscosity=1.8e-5, length_scale=1.0),
])
def test_reynolds_rejects_nonphysical_inputs(kwargs):
    with pytest.raises(ValueError):
        TurbulenceAnalyzer().calculate_reynolds(**kwargs)


def test_turbulence_closures_reject_negative_flow_scales():
    analyzer = TurbulenceAnalyzer()
    with pytest.raises(ValueError):
        analyzer.k_epsilon_model(1e6, -10.0, 1.0)
    with pytest.raises(ValueError):
        analyzer.les_model(1e6, 10.0, 0.0)


def test_hollow_section_rejects_wall_thickness_that_closes_section():
    with pytest.raises(ValueError):
        BladeRootGeometry().create_hollow_section(0.2, 0.1, 0.05)


def test_hertz_contact_rejects_nonpositive_radius():
    with pytest.raises(ValueError):
        BladeRootGeometry().hertz_contact_analysis(
            force=1000.0, radius1=0.0, radius2=0.02,
            young_modulus1=200e9, young_modulus2=70e9,
        )


def test_dovetail_rejects_impossible_top_width():
    with pytest.raises(ValueError):
        BladeRootGeometry().create_dovetail_profile(width=0.1, height=0.1, angle=45.0)


def test_reference_comparison_metrics_match_hand_calculation():
    metrics = compare(np.array([1.0, 2.0, 3.0]), np.array([1.0, 3.0, 2.0]))
    assert metrics["n"] == 3
    assert metrics["bias"] == pytest.approx(0.0)
    assert metrics["mae"] == pytest.approx(2.0 / 3.0)
    assert metrics["rmse"] == pytest.approx(np.sqrt(2.0 / 3.0))
    assert metrics["max_absolute_error"] == pytest.approx(1.0)


def test_reference_comparison_rejects_mismatched_shapes():
    with pytest.raises(ValueError):
        compare(np.array([1.0]), np.array([1.0, 2.0]))


def test_zero_stress_amplitude_has_infinite_s_n_life():
    material = StructuralMaterial(
        name="test steel", young_modulus=200e9, poisson_ratio=0.3,
        density=7850.0, yield_strength=350e6, ultimate_strength=600e6,
        endurance_strength=200e6,
    )
    assert np.isinf(FatigueEngine.sn_life(0.0, 0.0, material, "Goodman"))


def test_fatigue_rejects_mismatched_or_nonmonotonic_time_history():
    material = StructuralMaterial(
        name="test steel", young_modulus=200e9, poisson_ratio=0.3,
        density=7850.0, yield_strength=350e6, ultimate_strength=600e6,
        endurance_strength=200e6,
    )
    with pytest.raises(ValueError):
        FatigueEngine.evaluate(np.array([0.0, 1.0]), np.array([0.0]), material)
    with pytest.raises(ValueError):
        FatigueEngine.evaluate(np.array([0.0, 1.0]), np.array([1.0, 0.0]), material)


def test_fatigue_rejects_nonfinite_stress_history_and_unknown_correction():
    material = StructuralMaterial(
        name="test steel", young_modulus=200e9, poisson_ratio=0.3,
        density=7850.0, yield_strength=350e6, ultimate_strength=600e6,
        endurance_strength=200e6,
    )
    with pytest.raises(ValueError):
        FatigueEngine.rainflow(np.array([0.0, np.nan, 1.0]))
    with pytest.raises(ValueError):
        FatigueEngine.evaluate(np.array([0.0, 1.0]), np.array([0.0, 1.0]), material, correction="unknown")


def test_fir_tree_profile_respects_envelope_and_symmetry():
    profile = BladeRootGeometry().create_fir_tree_profile(width=0.4, height=0.12, num_teeth=3)
    assert profile.area > 0.0
    assert np.max(np.abs(profile.points[:, 0])) <= 0.4 / 2 + 1e-12
    assert np.min(profile.points[:, 1]) >= -1e-12
    assert np.max(profile.points[:, 1]) <= 0.12 + 1e-12
    assert profile.centroid[0] == pytest.approx(0.0, abs=1e-10)


def test_hollow_section_buckling_is_weaker_axis_controlled():
    geometry = BladeRootGeometry()
    section = geometry.create_hollow_section(outer_width=0.1, outer_height=0.3, wall_thickness=0.01, length=2.0)
    inner_w, inner_h = 0.08, 0.28
    ix = (0.1 * 0.3**3 - inner_w * inner_h**3) / 12.0
    iy = (0.3 * 0.1**3 - inner_h * inner_w**3) / 12.0
    assert section.critical_buckling_load == pytest.approx(np.pi**2 * 200e9 * min(ix, iy) / 2.0**2)


def test_polygon_centroid_and_inertia_match_rectangle_analytical_solution():
    geometry = BladeRootGeometry()
    rectangle = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 3.0], [0.0, 3.0]])
    assert geometry._polygon_area(rectangle) == pytest.approx(6.0)
    assert geometry._polygon_centroid(rectangle) == pytest.approx((1.0, 1.5))
    ix, iy = geometry._polygon_inertia(rectangle)
    assert ix == pytest.approx(2.0 * 3.0**3 / 12.0)
    assert iy == pytest.approx(3.0 * 2.0**3 / 12.0)


def test_polygon_centroid_is_orientation_invariant():
    geometry = BladeRootGeometry()
    points = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 3.0], [0.0, 3.0]])
    assert geometry._polygon_centroid(points) == pytest.approx(geometry._polygon_centroid(points[::-1]))
    profile = geometry.create_dovetail_profile(width=0.4, height=0.1, angle=45.0)
    assert profile.centroid[1] > 0.0
    assert profile.moment_inertia_xx > 0.0
    assert profile.section_modulus_xx > 0.0


def test_thermal_constraints_match_analytical_uniaxial_and_biaxial_stress():
    from blade_root_materials import ThermalAnalyzer
    database = MaterialDatabase()
    material = database.get_material("Steel_AISI_1040")
    analyzer = ThermalAnalyzer(database)
    temperature = 393.0
    delta_t = temperature - analyzer.room_temperature
    uniaxial = analyzer.analyze_thermal_effects("Steel_AISI_1040", temperature, 0.0, {"constraint_model": "uniaxial"})
    biaxial = analyzer.analyze_thermal_effects("Steel_AISI_1040", temperature, 0.0, {"constraint_model": "biaxial"})
    expected_uniaxial = material.young_modulus * material.thermal_expansion * delta_t
    expected_biaxial = expected_uniaxial / (1.0 - material.poisson_ratio)
    assert uniaxial.thermal_stress == pytest.approx([expected_uniaxial, 0.0, 0.0])
    assert biaxial.thermal_stress == pytest.approx([expected_biaxial, expected_biaxial, 0.0])
    assert biaxial.safety_factor == pytest.approx(material.yield_strength / expected_biaxial)


def test_free_thermal_expansion_has_no_thermal_stress():
    from blade_root_materials import ThermalAnalyzer
    result = ThermalAnalyzer(MaterialDatabase()).analyze_thermal_effects(
        "Steel_AISI_1040", 400.0, 0.0, {"constraint_model": "free"}
    )
    assert result.thermal_stress == pytest.approx([0.0, 0.0, 0.0])


def test_thermal_analysis_rejects_unknown_constraint_model():
    from blade_root_materials import ThermalAnalyzer
    with pytest.raises(ValueError):
        ThermalAnalyzer(MaterialDatabase()).analyze_thermal_effects(
            "Steel_AISI_1040", 400.0, 0.0, {"constraint_model": "unknown"}
        )


def test_airfoil_scaling_rejects_nonpositive_target_chord():
    with pytest.raises(ValueError):
        normalize_coordinates(symmetric_airfoil(), target_chord=0.0)
    with pytest.raises(ValueError):
        scale_coordinates(symmetric_airfoil(), target_chord=-1.0)


def test_airfoil_scaling_rejects_zero_chord_and_nonfinite_coordinates():
    degenerate = AirfoilCoordinates("zero-chord", np.ones(4), np.zeros(4), DATFormat.XFOIL)
    with pytest.raises(ValueError):
        normalize_coordinates(degenerate, target_chord=1.0)
    invalid = AirfoilCoordinates("nan-airfoil", np.array([0.0, 1.0]), np.array([0.0, np.nan]), DATFormat.XFOIL)
    with pytest.raises(ValueError):
        scale_coordinates(invalid, target_chord=1.0)


def test_hertzian_peak_pressure_matches_line_contact_formula():
    geometry = BladeRootGeometry()
    force, r1, r2, e1, e2, length = 1000.0, 0.02, 0.03, 200e9, 70e9, 0.1
    result = geometry.hertz_contact_analysis(force, r1, r2, e1, e2, length=length)
    effective_modulus = 1.0 / ((1.0 - 0.3**2) / e1 + (1.0 - 0.3**2) / e2)
    effective_radius = 1.0 / (1.0 / r1 + 1.0 / r2)
    half_width = np.sqrt(4.0 * force * effective_radius / (np.pi * effective_modulus * length))
    assert result.max_hertz_stress == pytest.approx(2.0 * force / (np.pi * half_width * length))
    assert result.max_hertz_stress > result.contact_pressure


def test_t_root_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        BladeRootGeometry().create_t_root_profile(width=0.2, height=0.1, flange_width=0.1)



def test_laminate_effective_in_plane_constants_come_from_extensional_compliance():
    database = MaterialDatabase()
    laminate = CompositeLaminate(database)
    result = laminate.create_symmetric_layup("Steel_AISI_1040", [0.0], 0.001)
    assert result.effective_young_x == pytest.approx(200e9, rel=1e-8)
    assert result.effective_young_y == pytest.approx(200e9, rel=1e-8)
    assert result.effective_shear == pytest.approx(77e9, rel=1e-8)
    assert result.effective_poisson_xy == pytest.approx(0.30, rel=1e-8)
