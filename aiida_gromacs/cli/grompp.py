#!/usr/bin/env python
"""CLI utility to run gmx grompp with AiiDA.

Usage: gmx_grompp --help
"""

import click
import os
from aiida import cmdline, engine
from aiida.plugins import DataFactory, CalculationFactory
from aiida_gromacs import helpers


def launch(gromacs_code, mdpfile, grofile, topfile, params):
    """Run grompp.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """
    if not gromacs_code:
        # get code
        computer = helpers.get_computer()
        gromacs_code = helpers.get_code(entry_point='gromacs',
                                        computer=computer)

    # Prepare input parameters
    GromppParameters = DataFactory('gromacs.grompp')
    parameters = GromppParameters(params)

    SinglefileData = DataFactory('core.singlefile')
    mdpfile = SinglefileData(file=os.path.join(os.getcwd(), mdpfile))
    grofile = SinglefileData(file=os.path.join(os.getcwd(), grofile))
    topfile = SinglefileData(file=os.path.join(os.getcwd(), topfile))

    # set up calculation
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'mdpfile': mdpfile,
        'grofile': grofile,
        'topfile': topfile,
        'metadata': {
            'description': 'grompp job submission with the aiida_gromacs plugin',
        },
    }

    # Note: in order to submit your calculation to the aiida daemon, do:
    # from aiida.engine import submit
    future = submit(CalculationFactory('gromacs'), **inputs)
    # result = engine.run(CalculationFactory('gromacs.grompp'), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
@click.option('-f', default='grompp.mdp', type=str, help="Input parameter file")
@click.option('-c', required=True, type=str, help="Input structure file")
@click.option('-p', default='topol.top', type=str, help="Topology file")
@click.option('-o', default='conf.gro', type=str, help="Output structure file")
def cli(code, f, c, p, o):
    """Run example.

    Example usage: 
    
    $ gmx_grompp --code gmx@localhost -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path): 
    
    $ gmx_grompp -f ions.mdp -c 1AKI_solvated.gro -p 1AKI_topology.top -o 1AKI_ions.tpr

    Help: $ gmx_grompp --help
    """
    
    # Place CLI params in a dict.
    params={'o': o,
           }

    launch(code, f, c, p, params)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
