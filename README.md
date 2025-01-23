# virtualtandem
A small library written in python to simulate a 2 wheeled vehicle in a virtual environment, with the aim of assisting in the tuning of control constants.

The TOML configuration file in the root folder, `robot_config.toml` is a file to be populated by the user of the library. You must define the following constants : 
<!-- List of constants -->

The configurations in virtualConfig are automatically set by the configuration program in `configure.py`. This file reads several csv formatted files to tune the dynamics of the internal components. This program requires that the following files exist:
<!-- List of files and how to generate -->

To generate the config files, the following programs exist:
<!-- List of programs to generate data -->