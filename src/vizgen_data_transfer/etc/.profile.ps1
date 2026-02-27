# PowerShell profile script to set up the development environment
# Added to $PROFILE so that it can be easily sourced when needed
# by running commands below in PowerShell:
# start_eivdt

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