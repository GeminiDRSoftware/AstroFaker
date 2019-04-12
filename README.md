# AstroFaker

Generate fake astronomical data to test DRAGONS.

## Description

The astrofaker package provides instrument-specific classes, derived from
the DRAGONS AstroData classes, that provide additional functionality to
permit the creation of simulated astronomical data for code testing.

It should be imported instead of gemini_instruments to ensure that all AstroData 
objects have the additional methods.

## Note

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.