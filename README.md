# Vizgen Data Transfer

This repository contains tools and scripts for managing data transfer processes related to Vizgen projects. It is designed to streamline and automate the movement of data between systems.


## Prerequisites

From Windows:
- Default Windows Python version

From Linux (for testing/debugging):
- Python 3.11 or higher

## Installation

1. Clone the repository:
    ```console
    git clone https://github.com/EI-CoreBioinformatics/vizgen_data_transfer.git
    cd vizgen_data_transfer
    ```
2. Build and Install using [Poetry](https://python-poetry.org/docs/#installation) (From Linux):
    ```console
    version=0.1.0
    poetry build
    pip install --prefix=/path/to/vizgen_data_transfer/${version}/x86_64 -U dist/*whl
    ```
3. Set up the environment (From Linux):
    ```console
    export PATH=/path/to/vizgen_data_transfer/${version}/x86_64/bin:$PATH
    export PYTHONPATH=/path/to/vizgen_data_transfer/${version}/x86_64/lib/python3*/site-packages:$PYTHONPATH
    ```
4. Run the script:

   From Windows:  
   Copy the script [vizgen_data_transfer.py](src/vizgen_data_transfer/vizgen_data_transfer.py) to `Windows F: Drive`, for example.
    ```console

    $ cd F:
    $ python .\vizgen_data_transfer.py --help
    
    usage: vizgen_data_transfer.py [-h] [--copy_type COPY_TYPE [COPY_TYPE ...]] [--threads THREADS] [--disk] [--debug] run_id
    
            Script for Vizgen data transfer
    
    
    positional arguments:
      run_id                Provide run name, for example: 202310261058_VZGEN1_VMSC10202
    
    options:
      -h, --help            show this help message and exit
      --copy_type COPY_TYPE [COPY_TYPE ...]
                            Provide copy type, for example: raw_data, analysis, output (default: ['raw_data', 'analysis', 'output'])
      --threads THREADS     Number of threads to use for copying (default: 8)
      --disk                Enable this option if run has to be copied from the Windows external Hard disk 'G:\Vizgen data Z drive' instead of the default Z: Drive on the analysis machine [default:False]
      --debug               Enable this option for debugging [default:False]
    
    Contact: Gemy George Kaithakottil (Gemy.Kaithakottil@earlham.ac.uk)
    ```
    
   From Linux (for testing/debugging):  
    ```console
    
    $ vizgen_data_transfer --help
    
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
   From Windows (`Windows PowerShell (x86)`):  
   Additional details are under the section 'Vizgen Data Transfer Script'  
   - Configure the settings in `F:\.vizgen_config.json`. Use template [vizgen_config.json](src/vizgen_data_transfer/etc/.vizgen_config.json)
   - Run the main script:
     ```console
     cd F:
     python .\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202
     ```

   From Linux (for testing/debugging):  
   - Configure the settings in `.vizgen_config.toml`. Use template [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml)
   - Run the main script:
      ```console
      vizgen_data_transfer --vizgen_config /path/to/.vizgen_config.toml 202310261058_VZGEN1_VMSC10202
      ```
## Glossary
Vizgen Windows PC
- The Vizgen Windows PC runs experiments and stores raw data on the `Windows D: Drive`. After completing an experiment, users initiate the analysis process, which automatically copies raw data to the `Analysis PC`. The `Analysis PC` carries out the analysis, generating analysis and output files.
- Use the `vizgen_data_transfer.py` script **with the JSON configuration file** on this Windows system.

Analysis PC
- The `Analysis PC` runs the analysis and stores raw data, analysis, and output files on the `Windows Z: Drive`.

Isilon Storage
- Isilon storage is a post-transfer destination for the `Analysis PC` data and is located on the `Windows F: Drive`.

External Hard Disk
- The `External Hard Disk` is a temporary storage location that currently holds data from the `Analysis PC`. This drive is located on the `Windows G: Drive`.


**Note:**  
The CLI tool `vizgen_data_transfer` using the **TOML configuration** - [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml), has only been tested on Linux systems. For Windows, please use `vizgen_data_transfer.py` with the **JSON configuration file** - [vizgen_config.json](src/vizgen_data_transfer/etc/.vizgen_config.json).

## Vizgen Data Transfer Script
Below are the steps to transfer Vizgen run data from the Analysis PC to the Isilon storage.

1. Open `Windows PowerShell (x86)` from the Vizgen Windows PC Start option.

2. Type in the following commands

    **Change to F: Drive**
    ```console
    cd F:
    ```

    **Initiate the transfer**
    ```console
    python .\vizgen_data_transfer.py RUN_FOLDER
    ```

    Replace `RUN_FOLDER` with the full run name, for example, `202310261058_VZGEN1_VMSC10202`

    Example command:
    ```console
    python .\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202
    ```

3. I have also added an option (`--disk`) whereby we can transfer Analysis data from the external hard disk if plugged into the Vizgen Windows PC. This option will copy the RUN_FOLDER from the external hard disk instead of the Analysis PC.

    An example command is below:
    ```console
    python .\vizgen_data_transfer.py --disk 202310261058_VZGEN1_VMSC10202
    ```

4. Once the data transfer is complete, the Python script will notify users via email (based on the list in the configuration file).


## What does the transfer script do?

The Python script `vizgen_data_transfer.py` is designed to copy data from the Analysis PC (or from the external hard disk) and write to the Isilon Storage

For example, when you execute the following command

```console
python .\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202
```

The script performs the following data transfer:

Raw data:
```console
Z:\merfish_raw_data\202310261058_VZGEN1_VMSC10202 to  F:\202310261058_VZGEN1_VMSC10202\raw_data
```
Analysis:
```console
Z:\merfish_analysis\202310261058_VZGEN1_VMSC10202 to F:\202310261058_VZGEN1_VMSC10202\analysis
```
Output:
```console
Z:\merfish_output\202310261058_VZGEN1_VMSC10202 to F:\202310261058_VZGEN1_VMSC10202\output
```
When specifying the `--disk` option, the script copies the data from the external hard disk (if connected) to the Isilon Storage

```console
python .\vizgen_data_transfer.py --disk 202310261058_VZGEN1_VMSC10202
```

Raw data:
```console
G:\Vizgen data Z drive\merfish_raw_data\RUN_FOLDER to  F:\RUN_FOLDER\raw_data
```
Analysis:
```console
G:\Vizgen data Z drive\merfish_analysis\RUN_FOLDER to F:\RUN_FOLDER\analysis
```
Output:
```console
G:\Vizgen data Z drive\merfish_output\RUN_FOLDER to F:\RUN_FOLDER\output
```

**Note:**  
The scripts use 8 CPUs as the default configuration for data transfer. If you need to increase the number of CPUs, for example, to 10 CPUs, you can use the option `--threads 10`. While I have not done specific tests to measure the impact of increasing the CPUs, this option allows you to adjust the CPU count if required.

For example:
```console
python .\vizgen_data_transfer.py --threads 10 RUN_FOLDER
```

## More transfer options?

If we are in a situation where the run data are in two different locations, i.e.,
- raw_data and analysis folders located on the Analysis PC, and
- output folder located on an External Hard Disk,
then you would need to execute the transfer command like below:

First, transfer the **raw_data** and **analysis** folders from the Analysis PC to the Isilon Storage

```console
python .\vizgen_data_transfer.py RUN_FOLDER
--copy_type raw_data analysis
```

Once the above command completes, transfer the **output** folder from the External Hard Disk to the Isilon Storage

```console
python .\vizgen_data_transfer.py RUN_FOLDER
--copy_type output
--disk
```

At the end of the transfer, we will have the below folder structure on the Isilon Storage.
```console
F:RUN_FOLDER/
├── raw_data    - Transferred from Analysis PC
├── analysis    - Transferred from Analysis PC
└── output      - Transferred from External Hard Disk
```


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the GNU General Public License. See the `LICENSE` file for details.

## Contact

For questions or support, please contact [Gemy.Kaithakottil@earlham.ac.uk] or [gemygk@gmail.com].
