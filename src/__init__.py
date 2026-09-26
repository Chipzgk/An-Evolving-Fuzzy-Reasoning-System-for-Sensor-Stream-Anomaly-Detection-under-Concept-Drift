"""Evolving Fuzzy Reasoning System for sensor-stream anomaly detection.

Modules extracted from notebooks 02-08 (logic kept identical so that the
frozen Phase 7/8 numbers are reproduced exactly):

- data       : dataset loading, sequential split, controlled drift / noise / missing injection
- fuzzy      : Mamdani FIS (5 inputs x 3 terms, 12 rules, centroid defuzzification)
- drift      : ADWIN wrapper (River)
- evolving   : buffer-based MF translation + prequential test-then-adapt runner
- evaluation : confusion-matrix metrics
"""
