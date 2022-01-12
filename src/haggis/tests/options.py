"""
Pytest plugin for processing the skg-specific command-line options.
"""

def pytest_addoption(parser):
    """
    Add options to the default command line.

    The following options are added:

    `--plots`
        Draw plots of x-values, y-values and fit comparisons. This
        option checks if matplotlib is installed, and issues a warning
        if not.

    """
    parser.addoption("--plots", action="store_true", default=False,
                     help="Generate graphical plots of input data")
