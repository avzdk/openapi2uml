# OpenAPI to UML Generator PowerShell Script
# Usage: .\run.ps1 [schema_directory] [filename] [format]
# Assumes virtual environment and dependencies are already set up

param(
    [string]$SchemaDir = ".",
    [string]$Filename = "uml_diagram",
    [ValidateSet("plantuml", "mermaid", "both")]
    [string]$Format = "both",
    [string]$Startclass = $null
)

Write-Host "OpenAPI to UML Generator" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Check if schema directory exists
if (-not (Test-Path $SchemaDir)) {
    Write-Host "ERROR: Schema directory '$SchemaDir' does not exist" -ForegroundColor Red
    exit 1
}
Write-Host "Running OpenAPI to UML Generator" -ForegroundColor Green
Write-Host "Schema directory: $SchemaDir" -ForegroundColor Cyan
Write-Host "Output filename: $Filename" -ForegroundColor Cyan
Write-Host "Output format: $Format" -ForegroundColor Cyan
Write-Host "Start class: $Startclass" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green

# Run the main program
if ($Startclass) {
    python main.py $SchemaDir --filename $Filename --format $Format --startclass $Startclass
} else {
    python main.py $SchemaDir --filename $Filename --format $Format
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Program failed to execute" -ForegroundColor Red
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
