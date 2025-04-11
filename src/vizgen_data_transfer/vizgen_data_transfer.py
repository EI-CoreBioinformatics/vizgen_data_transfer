#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for Vizgen data transfer

"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "Gemy.Kaithakottil@earlham.ac.uk"

# import libraries
import argparse
import os
import sys
import json
import logging
import subprocess
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# get script name
script = os.path.basename(sys.argv[0])
executed_command = " ".join(sys.argv)
# add python prefix to executed command
executed_command = "python " + executed_command

logging.basicConfig(
    format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG,
)


# Analysis drive - Z:
analysis_drive_pc = "Z:\\"
# Analysis drive disk - G:\Vizgen data Z drive
analysis_drive_pc_disk = "G:\\Vizgen data Z drive"
# Analysis drive debug - F:\test_data
analysis_drive_pc_debug = "F:\\test_data"
# for testing
analysis_drive_nix = "/ei/cb/development/kaithakg/vizgen/test_data"


# Isilon drive - F:
isilon_drive_pc = "F:\\"
# for testing
isilon_drive_nix = "/ei/cb/development/kaithakg/vizgen"

# robocopy exit codes
# ::: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy#exit-return-codes
robocopy_exit_codes = {
    0: "No files were copied. No failure was encountered. No files were mismatched. The files already exist in the destination directory; therefore, the copy operation was skipped.",
    1: "All files were copied successfully.",
    2: "There are some additional files in the destination directory that aren't present in the source directory. No files were copied.",
    3: "Some files were copied. Additional files were present. No failure was encountered.",
    5: "Some files were copied. Some files were mismatched. No failure was encountered.",
    6: "Additional files and mismatched files exist. No files were copied and no failures were encountered meaning that the files already exist in the destination directory.",
    7: "Files were copied, a file mismatch was present, and additional files were present.",
}


class VizgenDataTransfer:
    @staticmethod
    def get_operating_system():
        system_name = platform.system()
        return system_name.lower()

    def __init__(self, args):
        self.args = args
        self.run_id = args.run_id
        self.copy_type = [x.strip().lower() for x in args.copy_type]
        self.threads = args.threads
        self.disk = args.disk
        self.debug = args.debug

        self.store_copy_returns = dict()

        self.analysis_drive = None
        self.isilon_drive = None
        self.vizgen_config = None

        analysis_drive = analysis_drive_pc

        # set analysis Z: drive or external disk G: drive
        if self.disk:
            analysis_drive = analysis_drive_pc_disk

        # detect operating system
        self.os_name = self.get_operating_system()
        # set analysis drive and isilon drive
        if "windows" in self.os_name:
            logging.info("Operating System: Windows")
            self.analysis_drive = analysis_drive
            self.isilon_drive = isilon_drive_pc
            if self.debug:
                self.analysis_drive = analysis_drive_pc_debug
        elif "linux" in self.os_name:
            logging.info("Operating System: Linux")
            self.analysis_drive = analysis_drive_nix
            self.isilon_drive = isilon_drive_nix
        else:
            raise ValueError("Operating System: Unknown or not currenly supported")

        self.vizgen_config = (
            os.path.join(self.isilon_drive, ".vizgen_config.test.json")
            if self.debug
            else os.path.join(self.isilon_drive, ".vizgen_config.json")
        )

        # raise error if config file not found
        try:
            assert os.path.exists(self.vizgen_config)
        except AssertionError:
            logging.error(f"Error: Vizgen config file not found: {self.vizgen_config}")
            sys.exit(1)

        self.config = json.load(open(self.vizgen_config))

        logging.info(f"Config file: {self.vizgen_config}")

        self.analysis_drive_raw_data = os.path.join(
            self.analysis_drive, "merfish_raw_data", self.run_id
        )
        self.analysis_drive_analysis = os.path.join(
            self.analysis_drive, "merfish_analysis", self.run_id
        )
        self.analysis_drive_output = os.path.join(
            self.analysis_drive, "merfish_output", self.run_id
        )

        self.isilon_drive_raw_data = os.path.join(
            self.isilon_drive, self.run_id, "raw_data"
        )
        self.isilon_drive_analysis = os.path.join(
            self.isilon_drive, self.run_id, "analysis"
        )
        self.isilon_drive_output = os.path.join(
            self.isilon_drive, self.run_id, "output"
        )

        self.isilon_drive_raw_data_log = os.path.join(
            self.isilon_drive, self.run_id, "raw_data.log"
        )
        self.isilon_drive_analysis_log = os.path.join(
            self.isilon_drive, self.run_id, "analysis.log"
        )
        self.isilon_drive_output_log = os.path.join(
            self.isilon_drive, self.run_id, "output.log"
        )

    def check_run_folders(self):
        # input folder - Z:
        # raw_data
        # Z:\merfish_raw_data\202310261058_VZGEN1_VMSC10202
        # analysis
        # Z:\merfish_analysis\202310261058_VZGEN1_VMSC10202
        # output
        # Z:\merfish_output\202310261058_VZGEN1_VMSC10202
        # check if input folders exist and raise error if not
        if "raw_data" in self.copy_type and not os.path.exists(
            self.analysis_drive_raw_data
        ):
            raise ValueError(
                f"Error: Raw reads folder not found for run: {self.analysis_drive_raw_data}. If the folder exists elsewhere, i.e., on external hard disk, use the option --disk and specify which foldes(s) you need to copy from that location using the option --copy_type.\n\nHave a look at the options below:\n\nTo copy raw_data from analysis computer \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type raw_data\n\nTo copy analysis and output from external hard disk \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type analysis output --disk\n"
            )
        if "analysis" in self.copy_type and not os.path.exists(
            self.analysis_drive_analysis
        ):
            raise ValueError(
                f"Error: Analysis folder not found for run: {self.analysis_drive_analysis}. If the folder exists elsewhere, i.e., on external hard disk, use the option --disk and specify which foldes(s) you need to copy from that location using the option --copy_type.\n\nHave a look at the options below:\n\nTo copy raw_data from analysis computer \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type raw_data\n\nTo copy analysis and output from external hard disk \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type analysis output --disk\n"
            )
        if "output" in self.copy_type and not os.path.exists(
            self.analysis_drive_output
        ):
            raise ValueError(
                f"Error: Analysis output folder not found for run: {self.analysis_drive_output}. If the folder exists elsewhere, i.e., on external hard disk, use the option --disk and specify which foldes(s) you need to copy from that location using the option --copy_type.\n\nHave a look at the options below:\n\nTo copy raw_data from analysis computer \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type raw_data\n\nTo copy analysis and output from external hard disk \n\nExample: python .\\vizgen_data_transfer.py 202310261058_VZGEN1_VMSC10202 --copy_type analysis output --disk\n"
            )

        logging.info(f"All run folders exists for run: {self.run_id}")

    def copy_data(self, copy_type, source, destination, log_file):
        # robocopy command used:
        # robocopy
        # /Z - Copies files in restartable mode. In restartable mode, should a file copy be interrupted, robocopy can pick up where it left off rather than recopying the entire file.
        # /E - Copies subdirectories. This option automatically includes empty directories.
        # /J - copy using unbuffered I/O (recommended for large files).
        # /MT:8 - Creates multi-threaded copies with n threads. n must be an integer between 1 and 128. The default value for n is 8. For better performance, redirect your output using /log option.
        # /log+ - Writes the status output to the log file (overwrites the existing log file).
        cmd = None
        if self.os_name == "linux":
            cmd = f"rsync -av {source} {destination}"
        if self.os_name == "windows":
            cmd = f'robocopy "{source} " {destination} /Z /E /J /MT:{self.threads} /LOG+:{log_file}'

        logging.info(f"Command: {cmd}")

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            logging.info(f"STDOUT:\n{result.stdout}")
            if self.os_name == "linux":
                msg = f"Successfully copied {copy_type} for run: {self.run_id} with exit code '{result.returncode}'"
                logging.info(msg)
                self.store_copy_returns[copy_type] = msg
            if self.os_name == "windows":
                msg = f"Copied {copy_type} for run: {self.run_id} with robocopy exit code '{result.returncode}': {robocopy_exit_codes[result.returncode]}"
                logging.info(msg)
                self.store_copy_returns[copy_type] = msg
        except subprocess.CalledProcessError as e:
            logging.info(f"STDOUT:\n{e.stdout}")
            logging.error(f"{e}")
            logging.error(f"STDERR: {e.stderr}")
            if self.os_name == "linux":
                if e.returncode in [0]:
                    msg = f"Successfully copied {copy_type} for run: {self.run_id} with exit code '{e.returncode}'"
                    logging.info(msg)
                    self.store_copy_returns[copy_type] = msg
                else:
                    email_subject = (
                        f"Vizgen data transfer failed for run: {self.run_id}"
                    )
                    email_content = (
                        f"Vizgen data transfer failed for run: {self.run_id}"
                    )
                    error_msg = f"Error copying {copy_type} for run: {self.run_id}.\nExit code: '{e.returncode}'\nSTDERR: {e.stderr}Error: {e}"
                    email_content += f"\n\n{error_msg}"
                    email_content += f"\n\nCommand executed:\n\n{executed_command}"
                    self.send_email(email_subject, email_content)
                    raise ValueError(email_content)

            if self.os_name == "windows":
                if e.returncode in robocopy_exit_codes:
                    msg = f"Copied {copy_type} for run: {self.run_id} with robocopy exit code '{e.returncode}': {robocopy_exit_codes[e.returncode]}"
                    logging.info(msg)
                    self.store_copy_returns[copy_type] = msg
                else:
                    email_subject = (
                        f"Vizgen data transfer failed for run: {self.run_id}"
                    )
                    email_content = (
                        f"Vizgen data transfer failed for run: {self.run_id}"
                    )
                    error_msg = f"Error copying {copy_type} for run: {self.run_id}.\nExit code: '{e.returncode}'\nSTDERR: {e.stderr}Error: {e}"
                    email_content += f"\n\n{error_msg}"
                    email_content += f"\n\nCommand executed:\n\n{executed_command}"
                    self.send_email(email_subject, email_content)
                    raise ValueError(email_content)

    def check_log_file(self, log_file):
        header_valid = False
        footer_valid = False

        if self.os_name == "windows":
            # check if third line from the top of the log file
            header_format = "ROBOCOPY     ::     Robust File Copy for Windows"
            # check if 7th or 11th lines from the bottom of the log file
            footer_format = "Total    Copied   Skipped  Mismatch    FAILED    Extras"

            with open(log_file, "r") as f:
                lines = f.readlines()
                if len(lines) > 3:
                    logging.info(
                        f"Checking 3rd line from the top of log file: {log_file}"
                    )
                    logging.info(f"Required: '{header_format}'")
                    logging.info(f"Detected: '{lines[2].strip()}'")
                    if header_format in lines[2].strip():
                        header_valid = True
                    logging.info(f"Status:{header_valid}")
                if len(lines) > 11:
                    logging.info(
                        f"Checking 11th line from the bottom of log file: {log_file}"
                    )
                    logging.info(f"Required: '{footer_format}'")
                    logging.info(f"Detected: '{lines[-11].strip()}'")
                    if footer_format in lines[-11].strip():
                        footer_valid = True
                    logging.info(f"Status:{footer_valid}")
                if not footer_valid:
                    logging.info(
                        f"Checking 7th line from the bottom of log file: {log_file}"
                    )
                    if len(lines) > 7:
                        logging.info(f"Required: '{footer_format}'")
                        logging.info(f"Detected: '{lines[-7].strip()}'")
                        if footer_format in lines[-7].strip():
                            footer_valid = True
                        logging.info(f"Status:{footer_valid}")

        if self.os_name == "linux":
            # rsync log files are correctly formatted
            # hence no need to check header and footer
            header_valid = True
            footer_valid = True

        if header_valid and footer_valid:
            return "Complete log file"
        else:
            return "NOT A COMPLETE LOG FILE. PLEASE RE-RUN THE COMMAND TO GET A COMPLETE LOG FILE."

    def success_message(self):
        email_subject = f"Vizgen data transfer completed for run: {self.run_id}"
        email_content = f"Vizgen data transfer completed for run: {self.run_id}"
        log_content = str()
        logging.info(f"Vizgen data transfer completed for run: {self.run_id}")
        if "raw_data" in self.copy_type:
            email_content += f"\n - Raw directory: {self.isilon_drive_raw_data}"
            logging.info(f"Raw directory: {self.isilon_drive_raw_data}")
            log_content += f"\n - Raw directory: {self.check_log_file(self.isilon_drive_raw_data_log)}"
        if "analysis" in self.copy_type:
            email_content += f"\n - Analysis directory: {self.isilon_drive_analysis}"
            logging.info(f"Analysis directory: {self.isilon_drive_analysis}")
            log_content += f"\n - Analysis directory: {self.check_log_file(self.isilon_drive_analysis_log)}"
        if "output" in self.copy_type:
            email_content += f"\n - Output directory: {self.isilon_drive_output}"
            logging.info(f"Output directory: {self.isilon_drive_output}")
            log_content += f"\n - Output directory: {self.check_log_file(self.isilon_drive_output_log)}"
        # Add platform-specific message
        platform_msg = (
            "Any exit code value equal to or greater than 8 indicates that there was at least one failure during the robocopy operation."
            if self.os_name == "windows"
            else "Any non-zero exit code indicates that there was at least one failure during the rsync copy operation."
        )
        email_content += f"\n\nNote: {platform_msg}\n"
        logging.warning(f"Note: {platform_msg}")
        if "raw_data" in self.copy_type:
            if "raw_data" in self.store_copy_returns:
                email_content += (
                    f"\n - Raw directory: {self.store_copy_returns['raw_data']}"
                )
                logging.info(f"Raw directory: {self.store_copy_returns['raw_data']}")
        if "analysis" in self.copy_type:
            if "analysis" in self.store_copy_returns:
                email_content += (
                    f"\n - Analysis directory: {self.store_copy_returns['analysis']}"
                )
                logging.info(
                    f"Analysis directory: {self.store_copy_returns['analysis']}"
                )
        if "output" in self.copy_type:
            if "output" in self.store_copy_returns:
                email_content += (
                    f"\n - Output directory: {self.store_copy_returns['output']}"
                )
                logging.info(f"Output directory: {self.store_copy_returns['output']}")
        if log_content:
            email_content += f"\n\n\nLog file status:\n{log_content}"

            # change email_subject completed to failed if NOT A COMPLETE LOG FILE detected in log_content
            if "NOT A COMPLETE LOG FILE" in log_content:
                email_subject = email_subject.replace("completed", "failed")

        email_content += f"\n\nCommand executed:\n\n{executed_command}"
        self.send_email(email_subject, email_content)

    def send_email(self, email_subject, email_content):
        # send email

        smtp_server = self.config["smtp_server"]
        sender_email = self.config["sender_email"]
        addressees = []
        addressees = self.config["addressees"]

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart("alternative")
        part1 = MIMEText(email_content, "plain")
        msg["Subject"] = email_subject
        msg["From"] = sender_email
        msg["To"] = "To: " + "; ".join(str(x) for x in addressees)
        msg.attach(part1)

        logging.info(f"Sending email to: {str(addressees)}")

        s = smtplib.SMTP(smtp_server)
        maildelivery = s.sendmail(msg["From"], addressees, msg.as_string())

        if not bool(maildelivery):
            logging.info("Email sent successfully")
        else:
            logging.error("Email delivery failed")

    def transfer_run(self):
        # check if run folders exist and raise error if not
        if not os.path.exists(self.isilon_drive_raw_data):
            logging.info(
                f"Creating raw_data folder for run: {self.isilon_drive_raw_data}"
            )
            os.makedirs(self.isilon_drive_raw_data)
        if not os.path.exists(self.isilon_drive_analysis):
            logging.info(
                f"Creating analysis folder for run: {self.isilon_drive_analysis}"
            )
            os.makedirs(self.isilon_drive_analysis)
        if not os.path.exists(self.isilon_drive_output):
            logging.info(f"Creating output folder for run: {self.isilon_drive_output}")
            os.makedirs(self.isilon_drive_output)

        # copy raw_data
        if "raw_data" in self.copy_type:
            logging.info(
                f"Copying raw_data from {self.analysis_drive_raw_data} to {self.isilon_drive_raw_data}"
            )
            # copy raw_data from analysis drive to isilon drive
            # robocopy Z:\merfish_raw_data\202310261058_VZGEN1_VMSC10202 F:202310261058_VZGEN1_VMSC10202\raw_data /E /MT:8
            self.copy_data(
                "raw_data",
                self.analysis_drive_raw_data,
                self.isilon_drive_raw_data,
                self.isilon_drive_raw_data_log,
            )

        # copy analysis
        if "analysis" in self.copy_type:
            logging.info(
                f"Copying analysis from {self.analysis_drive_analysis} to {self.isilon_drive_analysis}"
            )
            # copy analysis from analysis drive to isilon drive
            # robocopy Z:\merfish_analysis\202310261058_VZGEN1_VMSC10202 F:202310261058_VZGEN1_VMSC10202\analysis /E /MT:8
            self.copy_data(
                "analysis",
                self.analysis_drive_analysis,
                self.isilon_drive_analysis,
                self.isilon_drive_analysis_log,
            )

        # copy output
        if "output" in self.copy_type:
            logging.info(
                f"Copying output from {self.analysis_drive_output} to {self.isilon_drive_output}"
            )
            # copy output from analysis drive to isilon drive
            # robocopy Z:\merfish_output\202310261058_VZGEN1_VMSC10202 F:202310261058_VZGEN1_VMSC10202\output /E /MT:8
            self.copy_data(
                "output",
                self.analysis_drive_output,
                self.isilon_drive_output,
                self.isilon_drive_output_log,
            )

        # check if output folders exist and raise error if not
        if not os.path.exists(self.isilon_drive_raw_data):
            raise ValueError(
                f"Error: Raw reads folder not found for run: {self.isilon_drive_raw_data}. Looks like copy failed. Simply restart the command to resume copy from where it left off."
            )
        if not os.path.exists(self.isilon_drive_analysis):
            raise ValueError(
                f"Error: Analysis folder not found for run: {self.isilon_drive_analysis}. Looks like copy failed. Simply restart the command to resume copy from where it left off."
            )
        if not os.path.exists(self.isilon_drive_output):
            raise ValueError(
                f"Error: Analysis output folder not found for run: {self.isilon_drive_output}. Looks like copy failed. Simply restart the command to resume copy from where it left off."
            )

        self.success_message()

        # output folder - F:
        # output structure
        # raw_data
        # F:202310261058_VZGEN1_VMSC10202\raw_data
        # analysis
        # F:202310261058_VZGEN1_VMSC10202\analysis
        # output
        # F:202310261058_VZGEN1_VMSC10202\output

    def run(self):
        logging.info(f"Processing run: {self.run_id}")
        self.check_run_folders()
        self.transfer_run()
        logging.info("Command executed: " + executed_command)
        logging.info("Analysis complete")


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    pass


def main():
    parser = argparse.ArgumentParser(
        prog=script,
        formatter_class=HelpFormatter,
        description="""
        Script for Vizgen data transfer
        """,
        epilog=f"Contact: {__author__} ({__email__})",
    )
    parser.add_argument(
        "run_id",
        help="Provide run name, for example: 202310261058_VZGEN1_VMSC10202",
    )
    # whether to copy raw_data, analysis, output or all
    parser.add_argument(
        "--copy_type",
        nargs="+",
        default=["raw_data", "analysis", "output"],
        help="Provide copy type, for example: raw_data, analysis, output",
    )
    # add threads option
    parser.add_argument(
        "--threads",
        default=8,
        help="Number of threads to use for copying",
    )
    parser.add_argument(
        "--disk",
        action="store_true",
        help="Enable this option if run has to be copied from the Windows external Hard disk 'G:\\Vizgen data Z drive' instead of the default Z: Drive on the analysis machine [default:%(default)s]",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable this option for debugging [default:%(default)s]",
    )
    args = parser.parse_args()
    VizgenDataTransfer(args).run()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
