# Mahras components covered by this evidence repository

This document describes the product areas represented in the current evidence snapshot. It is not a complete product specification.

## Solar site and PV analysis

The included evidence covers selected solar-resource, plane-of-array irradiance and PV-yield calculations, including comparisons with PVGIS and Open-Meteo-derived data. The report packages distinguish weather inputs, irradiance transposition, time alignment and annual-yield calculations.

The presence of a comparison report does not mean that every site-analysis feature or every equipment configuration has been validated. See the individual report and the limitations document.

## Airfoil-CAD and rotor engineering

The included Airfoil-CAD material covers selected backend regression tests and documentation for airfoil geometry, BEM analysis, composite failure calculations and related structural checks. The evidence includes a test runner and a reference-data plan.

The current snapshot does not establish a complete experimental validation of the full rotor-design workflow. Some model assumptions and unimplemented effects are documented in the BEM and composite review notes.

## Weather data ingestion

The weather package covers test fixtures for station-data import and quality-control behaviour. Its CSV samples are synthetic and should not be used as climate data or sensor-performance evidence.

## Wind resource, wakes and CFD

This repository does not yet contain a complete independent experimental validation package for wind-resource estimation, wake modelling or CFD flow fields. Any future results in these areas should include matched reference measurements, domain and mesh sensitivity, boundary conditions, convergence evidence and uncertainty.

## Scope discipline

Only components represented by linked evidence should be described as validated. A product feature being present in the Mahras application, or having a software test, is not enough to claim that its engineering predictions have been experimentally validated.
