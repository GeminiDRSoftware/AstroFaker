                 _        _             _____     _
                / \   ___| |_ _ __ ___ |  ___|_ _| | _____ _ __
               / _ \ / __| __| '__/ _ \| |_ / _` | |/ / _ \ '__|
              / ___ \\__ \ |_| | | (_) |  _| (_| |   <  __/ |
             /_/   \_\___/\__|_|  \___/|_|  \__,_|_|\_\___|_|

               Produce simulated astronomical data for DRAGONS

## Purpose

The AstroFaker module provides instrument-specific classes, derived from
the DRAGONS AstroData classes, that provide additional functionality to
permit the creation of simulated astronomical data for code testing.

The AstroFaker module should be imported instead of gemini_instruments to
ensure that all AstroData objects have the additional methods.