# OpenAPI to UML Generator PowerShell Script
# Usage: .\run.ps1 [schema_directory] [filename] [format]
# Assumes virtual environment and dependencies are already set up

param(
    [string]$SchemaDir = "data\schemas",
    [string]$Filename = "diagram",
    [ValidateSet("plantuml", "mermaid", "both")]
    [string]$Format = "both"
)

Write-Host "OpenAPI to UML Generator" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Check if schema directory exists
if (-not (Test-Path $SchemaDir)) {
    Write-Host "ERROR: Schema directory '$SchemaDir' does not exist" -ForegroundColor Red
    Write-Host "Available directories:" -ForegroundColor Yellow
    if (Test-Path "data\schemas") { Write-Host "  - data\schemas" -ForegroundColor Cyan }
    if (Test-Path "data_1\schemas") { Write-Host "  - data_1\schemas" -ForegroundColor Cyan }
    Write-Host ""
    Write-Host "Usage: .\run.ps1 [schema_directory] [filename] [format]" -ForegroundColor Yellow
    Write-Host "Example: .\run.ps1 data\schemas my_diagram mermaid" -ForegroundColor Yellow
    Write-Host "Formats: plantuml, mermaid, both" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Running OpenAPI to UML Generator" -ForegroundColor Green
Write-Host "Schema directory: $SchemaDir" -ForegroundColor Cyan
Write-Host "Output filename: $Filename" -ForegroundColor Cyan
Write-Host "Output format: $Format" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Run the main program
python main.py $SchemaDir --filename $Filename --format $Format

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Program failed to execute" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Generation completed successfully!" -ForegroundColor Green
Write-Host ""
if (Test-Path "$Filename.puml") { Write-Host "PlantUML file: $Filename.puml" -ForegroundColor Cyan }
if (Test-Path "$Filename.png") { Write-Host "PNG diagram: $Filename.png" -ForegroundColor Cyan }
if (Test-Path "$Filename.mmd") { Write-Host "Mermaid file: $Filename.mmd" -ForegroundColor Cyan }
Write-Host "================================================" -ForegroundColor Green

# Keep window open to see results
Read-Host "Press Enter to exit"
