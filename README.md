# Vizgen Data Transfer

This repository contains tools and scripts for managing data transfer processes related to Vizgen projects. It is designed to streamline and automate the movement of data between systems.


## Prerequisites

- Python 3.11 or higher
- Required Python packages listed in `pyproject.toml`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/EI-CoreBioinformatics/vizgen_data_transfer.git
    cd vizgen_data_transfer
    ```
2. Build and Install using [Poetry](https://python-poetry.org/docs/#installation):
    ```bash
    version=0.1.0
    poetry build
    pip install --prefix=/path/to/vizgen_data_transfer/${version}/x86_64 -U dist/*whl
    ```
3. Set up the environment:
    ```bash
    export PATH=/path/to/vizgen_data_transfer/${version}/x86_64/bin:$PATH
    export PYTHONPATH=/path/to/vizgen_data_transfer/${version}/x86_64/lib/python3*/site-packages:$PYTHONPATH
    ```
4. Run the script:
    ```bash
    vizgen_data_transfer --help
    usage: vizgen_data_transfer [-h] [--copy_type COPY_TYPE [COPY_TYPE ...]] [--threads THREADS] [--disk] [--vizgen_config VIZGEN_CONFIG] [--debug] run_id

            Script for Vizgen data transfer


    positional arguments:
    run_id                Provide run name, for example: 202310261058_VZGEN1_VMSC10202

    options:
    -h, --help            show this help message and exit
    --copy_type COPY_TYPE [COPY_TYPE ...]
                            Provide copy type, for example: raw_data, analysis, output (default: ['raw_data', 'analysis', 'output'])
    --threads THREADS     Number of threads to use for copying (default: 8)
    --disk                Enable this option if run has to be copied from the Windows external Hard disk 'G:\Vizgen data Z drive' instead of the default Z: Drive on the analysis machine [default:False]
    --vizgen_config VIZGEN_CONFIG
                            Path to vizgen config file [default:/path/to/vizgen_data_transfer/dev/x86_64/lib/python3*/site-packages/vizgen_data_transfer/etc/.vizgen_config.toml]
    --debug               Enable this option for debugging [default:False]

    Contact: Gemy George Kaithakottil (Gemy.Kaithakottil@earlham.ac.uk)
    ```

## Usage

1. Configure the settings in `.vizgen_config.toml`.
2. Run the main script:
    ```bash
    vizgen_data_transfer --vizgen_config /path/to/.vizgen_config.toml 202310261058_VZGEN1_VMSC10202
    ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the GNU General Public License. See the `LICENSE` file for details.

## Contact

For questions or support, please contact [Gemy.Kaithakottil@earlham.ac.uk] or [gemygk@gmail.com].
