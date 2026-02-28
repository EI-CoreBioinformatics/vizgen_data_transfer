# Vizgen Data Transfer

This repository contains tools and scripts for managing data transfer processes related to Vizgen projects. It is designed to streamline and automate the movement of data from Vizgen MERSCOPE and Vizgen MERSCOPE Ultra instruments to the Isilon storage, ensuring efficient and reliable data handling.


## Prerequisites

From Windows:
- Default Windows Python version (Tested on Python 3.9.13)
- Tested on both Vizgen MERSCOPE and Vizgen MERSCOPE Ultra instruments

From Linux (for testing/debugging):
- Tested on Python 3.11 or higher
- Should work with Python 3.9 or higher, but not yet tested on Python 3.9

## Installation

### Vizgen Instrument Windows PC

1. Create a Python virtual environment and activate it:
    ```console
    # For Windows PowerShell (x86)
    # Note: Install the virtual environment outside the Vizgen drives.
    # For example, the L: drive is located in the Isilon storage.
    PS C:\Users\Merscope3> cd L:\
    PS L:\> python -m venv eivdt
    Actual environment location may have moved due to redirects, links or junctions.
        Requested location: "L:\eivdt\Scripts\python.exe"
        Actual location:    "\\institute-lab-data\asset_number\eivdt\Scripts\python.exe"

    # Activate the virtual environment
    PS L:\> eivdt\Scripts\Activate.ps1
    (eivdt) PS L:\>
    ```
    See below for instructions on setting up the PROFILE in Windows PowerShell (x86) to simplify virtual environment activation - [here](#create-profile)

2. Install [UV](https://docs.astral.sh/uv/) in the virtual environment:
    ```console
    (eivdt) PS L:\> pip install uv
    ```

3. Clone the repository:
    ```console
    (eivdt) PS L:\> mkdir vizgen_data_transfer
    (eivdt) PS L:\> cd .\vizgen_data_transfer\
    (eivdt) PS L:\vizgen_data_transfer> git clone https://github.com/EI-CoreBioinformatics/vizgen_data_transfer.git src
    (eivdt) PS L:\vizgen_data_transfer> cd src
    (eivdt) PS L:\vizgen_data_transfer\src> git checkout tags/v0.1.0
    ```
4. Build and install using UV:
    ```console
    (eivdt) PS L:\vizgen_data_transfer\src> uv build
    (eivdt) PS L:\vizgen_data_transfer\src> pip install --force-reinstall -U .\dist\vizgen_data_transfer-0.1.0-py3-none-any.whl
    ```

5. Run the script:

    ```console

    (eivdt) PS L:\> vizgen_data_transfer -h
    usage: vizgen_data_transfer.exe [-h] [--copy_type COPY_TYPE [COPY_TYPE ...]] [--threads THREADS] [--disk]
                                    [--vizgen_config VIZGEN_CONFIG] [--debug]
                                    run_id

            Script for Vizgen data transfer


    positional arguments:
    run_id                Provide run name, for example: 202310261058_VZGEN1_VMSC10202

    optional arguments:
    -h, --help            show this help message and exit
    --copy_type COPY_TYPE [COPY_TYPE ...]
                            Provide copy type, for example: raw_data, analysis, output (default: ['raw_data', 'analysis', 'output'])
    --threads THREADS     Number of threads to use for copying (default: 8)
    --disk                Enable this option if run has to be copied from the Windows external Hard disk 'G:\Vizgen data Z drive' instead of the default Z: Drive on the analysis machine [default:False]
    --vizgen_config VIZGEN_CONFIG
                            Path to vizgen config file [default:L:\.vizgen_config.toml]
    --debug               Enable this option for debugging [default:False]

    Contact: Gemy George Kaithakottil (Gemy.Kaithakottil@earlham.ac.uk)
    ```

**Important Note (Windows Config File)**:

By default on Windows, the script expects the `--vizgen_config` TOML file to be located in the working directory from which the script is executed (in this case, `L:\`).

You can copy the template configuration file:
- [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml)

to

```console
L:\.vizgen_config.toml
```

If you prefer to keep the config file in another location, specify its path using the `--vizgen_config` option:

```console
vizgen_data_transfer --vizgen_config L:\config_files\.vizgen_config.toml 202310261058_VZGEN1_VMSC10202
```

### Linux (Testing / Debugging)

1. Clone the repository:
    ```console
    git clone https://github.com/EI-CoreBioinformatics/vizgen_data_transfer.git
    cd vizgen_data_transfer
    git checkout tags/v0.1.0
    ```
2. Build and install using [UV](https://docs.astral.sh/uv/):
    ```console
    version=0.1.0
    uv build
    pip install --prefix=/path/to/vizgen_data_transfer/${version}/x86_64 -U dist/*whl
    ```
3. Set up the environment:
    ```console
    export PATH=/path/to/vizgen_data_transfer/${version}/x86_64/bin:$PATH
    export PYTHONPATH=/path/to/vizgen_data_transfer/${version}/x86_64/lib/python3*/site-packages:$PYTHONPATH
    ```
4. Run the script:

    ```console
    $ vizgen_data_transfer --help
    ```

## Usage

### Vizgen Instrument Windows PC
<a name="create-profile"></a>
For ease of use, it is recommended to create a PROFILE in `Windows PowerShell (x86)` that:
- Activates the virtual environment
- Sets the working directory to `L:\` (or your preferred execution drive)

This eliminates the need to manually activate the environment each time.

The template [PROFILE](src/vizgen_data_transfer/etc/.profile.ps1) can be used to set up the profile for the Vizgen Windows PC. 

**Create a PROFILE**

Check if a PROFILE already exists, if not create a new one
```console
PS C:\Users\Merscope3> Test-Path $PROFILE
False
PS C:\Users\Merscope3> New-Item -ItemType File -Path $PROFILE -Force
```

Edit the PROFILE using notepad
```console
PS C:\Users\Merscope3> notepad $PROFILE
```

Add to the PROFILE
```console
# Profile for activating Vizgen Data Transfer environment
# Added on 26/02/2026
# Contact: Gemy.Kaithakottil@earlham.ac.uk

function EIVDT_Project {
    # Location of the python virtual environment
    $ProjectRoot = "L:\"

    # Name of the virtual environment
    $VenvName = "eivdt"

    # 1. Change to the project directory
    Set-Location -Path $ProjectRoot

    # 2. Activate the virtual environment
    . ".\$VenvName\Scripts\Activate.ps1"

    Write-Host "`n Environment '$VenvName' activated. You are now on drive L:`n" -ForegroundColor Green
}

# Optional: Create a short alias for the function
Set-Alias -Name start_eivdt -Value EIVDT_Project
```


Test and reload the PROFILE

```console
PS C:\Users\Merscope3> Test-Path $PROFILE
True
PS C:\Users\Merscope3> . $PROFILE
```

Start the new environment using the alias created in the PROFILE, as explained above [here](#create-profile)
```console
PS L:\> start_eivdt

 Environment 'eivdt' activated. You are now on drive L:
```

Run the script from the new environment
- Configure the settings in the `vizgen_config.toml`. Use template config file [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml)

- Execute the script using the command below. Replace `RUN_FOLDER` with the full run name, for example, `202310261058_VZGEN1_VMSC10202`
    ```console

    (eivdt) PS L:\> vizgen_data_transfer RUN_FOLDER
    ```

From Linux (for testing/debugging):
- Configure the settings in `.vizgen_config.toml`. Use template [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml)
- Run the main script:
    ```console
    vizgen_data_transfer --vizgen_config /path/to/.vizgen_config.toml RUN_FOLDER
    ```

## Glossary
Vizgen Windows PC
- The Vizgen Windows PC runs experiments and stores raw data on the `Windows D: Drive`. After completing an experiment, users initiate the analysis process, which automatically copies raw data to the `Analysis Network Drive`. The `Analysis Network Drive` carries out the analysis, generating analysis and output files.

Analysis Network Drive
- The `Analysis Network Drive` runs the analysis and stores raw data, analysis, and output files on the `Windows Z: Drive`.

Isilon Storage
- Isilon storage is a final storage location where the raw data, analysis, and output files are transferred to from the `Analysis Network Drive` using the `vizgen_data_transfer` script. The Isilon storage is mounted as the `Windows L: Network Drive` on the Vizgen Windows PC.

External Hard Disk
- The `External Hard Disk` is a temporary storage location that holds data from the `Analysis Network Drive`. This drive is located on the `Windows G: Drive`.


## Vizgen Data Transfer Script
Below are the steps to transfer Vizgen run data from the Analysis Network Drive to the Isilon storage.

1. Open `Windows PowerShell (x86)` from the Vizgen Windows PC Start option.

2. Type in the following commands

    **Start the new environment using the alias created in the PROFILE**
    ```console
    start_eivdt
    ```

    **Initiate the transfer**
    ```console
    vizgen_data_transfer RUN_FOLDER
    ```

    Replace `RUN_FOLDER` with the full run name, for example, `202310261058_VZGEN1_VMSC10202`

    Example command:
    ```console
    vizgen_data_transfer 202310261058_VZGEN1_VMSC10202
    ```

3. I have also added an option (`--disk`) whereby we can transfer Analysis data from the external hard disk if plugged into the Vizgen Windows PC. This option will copy the RUN_FOLDER from the external hard disk instead of the Analysis Network Drive.

    An example command is below:
    ```console
    vizgen_data_transfer --disk 202310261058_VZGEN1_VMSC10202
    ```

4. Once the data transfer is complete, the Python script will notify users via email (based on the list in the configuration file).

    An example email content is below:

    **Note**
    I check for the data transfer summary using both Python-based counts and Robocopy-based counts. The Python-based counts are obtained by traversing the source and destination directories before and after the transfer, while the Robocopy-based counts are obtained from the Robocopy log files generated separately during the transfer process (using Robocopys /L option as you can see in the value `robocopy_list` of config file [vizgen_config.toml](src/vizgen_data_transfer/etc/.vizgen_config.toml)). This dual approach allows for cross-validation of the transfer results, ensuring that the data transfer was successful and that there are no discrepancies in the file counts or sizes between the source and destination directories.

    Robocopy always returns one extra folder count in the log file compared to the Python-based folder count because Robocopy counts the root source and destination folders as part of the total folder count, while the Python-based method only counts the subfolders within the source and destination directories. Therefore, when comparing the folder counts from both methods, it is expected to see one additional folder in the Robocopy-based counts due to this difference in counting methodology.

    ```console
    Subject: Vizgen data transfer completed for run: 202310261058_VZGEN1_VMSC10202

    Vizgen data transfer completed for run: 202310261058_VZGEN1_VMSC10202

    Data location(s):

    - Raw directory: L:\202310261058_VZGEN1_VMSC10202\raw_data
    - Analysis directory: L:\202310261058_VZGEN1_VMSC10202\analysis
    - Output directory: L:\202310261058_VZGEN1_VMSC10202\output

    Data summary:

    Data summary Python based counts:

    Raw_Data Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 8042              11                838.861           900719884237     
    After Transfer  8042              11                838.861           900719884237     
    ----------------------------------------------------------------------------------------


    Data summary Robocopy based counts:

    Raw_Data Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 8042              12                838.861           900719884237     
    After Transfer  8042              12                838.861           900719884237     
    ----------------------------------------------------------------------------------------


    Data summary Python based counts:

    Analysis Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 123787            1567              845.673           908034287581     
    After Transfer  123787            1567              845.673           908034287581     
    ----------------------------------------------------------------------------------------


    Data summary Robocopy based counts:

    Analysis Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 123787            1568              845.673           908034287581     
    After Transfer  123787            1568              845.673           908034287581     
    ----------------------------------------------------------------------------------------


    Data summary Python based counts:

    Output Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 43                4                 108.551           116555448991     
    After Transfer  43                4                 108.551           116555448991     
    ----------------------------------------------------------------------------------------


    Data summary Robocopy based counts:

    Output Transfer Summary
    ----------------------------------------------------------------------------------------
    Status          Total Files       Total Folders     Total Size (GB)   Total Size (Bytes)
    ----------------------------------------------------------------------------------------
    Before Transfer 43                5                 108.551           116555448991     
    After Transfer  43                5                 108.551           116555448991     
    ----------------------------------------------------------------------------------------


    Exit code(s):

    Note: Any exit code value equal to or greater than 8 indicates that there was at least one failure during the robocopy operation.

    - Raw directory: Copied raw_data for run: 202310261058_VZGEN1_VMSC10202 with robocopy exit code '0': No files were copied. No failure was encountered. No files were mismatched. The files already exist in the destination directory; therefore, the copy operation was skipped.
    - Analysis directory: Copied analysis for run: 202310261058_VZGEN1_VMSC10202 with robocopy exit code '0': No files were copied. No failure was encountered. No files were mismatched. The files already exist in the destination directory; therefore, the copy operation was skipped.
    - Output directory: Copied output for run: 202310261058_VZGEN1_VMSC10202 with robocopy exit code '0': No files were copied. No failure was encountered. No files were mismatched. The files already exist in the destination directory; therefore, the copy operation was skipped.

    Log file status:

    - Raw directory: Complete log file
    - Analysis directory: Complete log file
    - Output directory: Complete log file

    Command executed:

    python L:\eivdt\Scripts\vizgen_data_transfer.exe 202310261058_VZGEN1_VMSC10202
    ```


## What does the transfer script do?

The `vizgen_data_transfer` script:
- Copies data from the Analysis Network Drive or external disk
- Writes data to Isilon Storage
- Uses:
  - robocopy on Windows
  - rsync on Linux
- Generates transfer logs
- Sends email notifications upon completion


For example, when you execute the following command

```console
vizgen_data_transfer 202310261058_VZGEN1_VMSC10202
```

The script performs the following data transfer:

Raw data:
```console
Z:\merfish_raw_data\202310261058_VZGEN1_VMSC10202 to  L:\202310261058_VZGEN1_VMSC10202\raw_data
```
Analysis:
```console
Z:\merfish_analysis\202310261058_VZGEN1_VMSC10202 to L:\202310261058_VZGEN1_VMSC10202\analysis
```
Output:
```console
Z:\merfish_output\202310261058_VZGEN1_VMSC10202 to L:\202310261058_VZGEN1_VMSC10202\output
```
When specifying the `--disk` option, the script copies the data from the external hard disk (if connected) to the Isilon Storage

```console
vizgen_data_transfer --disk 202310261058_VZGEN1_VMSC10202
```

Raw data:
```console
G:\Vizgen data Z drive\merfish_raw_data\RUN_FOLDER to  L:\RUN_FOLDER\raw_data
```
Analysis:
```console
G:\Vizgen data Z drive\merfish_analysis\RUN_FOLDER to L:\RUN_FOLDER\analysis
```
Output:
```console
G:\Vizgen data Z drive\merfish_output\RUN_FOLDER to L:\RUN_FOLDER\output
```

**Note:**  
The scripts use 1 CPU as the default configuration for data transfer. If you need to increase the number of CPUs, for example, to 8 CPUs, you can use the option `--threads 8`. Our testing has shown incomplete transfers using multiple CPUs requiring restart of the transfer, hence the default is set to 1 CPU. If you want to use multiple CPUs, you can specify the number of threads like below:

For example:
```console
vizgen_data_transfer --threads 8 202310261058_VZGEN1_VMSC10202
```

## More transfer options?

If we are in a situation where the run data are in two different locations, i.e.,
- raw_data and analysis folders located on the Analysis Network Drive, and
- output folder located on an External Hard Disk,
then you would need to execute the transfer command like below:

First, transfer the **raw_data** and **analysis** folders from the Analysis Network Drive to the Isilon Storage

```console
vizgen_data_transfer RUN_FOLDER \
    --copy_type raw_data analysis
```

Once the above command completes, transfer the **output** folder from the External Hard Disk to the Isilon Storage

```console
vizgen_data_transfer RUN_FOLDER \
    --copy_type output \
    --disk
```

At the end of the transfer, we will have the below folder structure on the Isilon Storage.
```console
L:RUN_FOLDER/
├── raw_data    - Transferred from Analysis Network Drive
├── analysis    - Transferred from Analysis Network Drive
└── output      - Transferred from External Hard Disk
```


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the GNU General Public License. See the `LICENSE` file for details.

## Contact

For questions or support, please contact [Gemy.Kaithakottil@earlham.ac.uk] or [gemygk@gmail.com].
