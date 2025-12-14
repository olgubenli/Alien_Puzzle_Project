$notebooks = @{
    "Notebook_2.ipynb" = @("yenimatrisgunceldb.py", "anayolyanyoltop10.py", "icbaglantilarladuraklar.py", "equjmesafeler.py", "k7top5icin.py", "kontrol56top20icin.py")
    "Notebook_3.ipynb" = @("yenigrafik49.py", "yenigrafik50.py", "piegrafik18.py", "bigpie20590grafik6.py", "violingrafik.py", "historgram1bucuk.py")
    "Notebook_4.ipynb" = @("3dgrafik31.py", "networkgrafikhat5.py", "dunyadanmesafe.py", "sonuckontrol.py", "strestestison6.py")
}

$srcDir = Get-Location
$outDir = Join-Path (Get-Item $srcDir).Parent.FullName "notebooks"


# Ensure output directory exists
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

foreach ($nbName in $notebooks.Keys) {
    Write-Host "Processing $nbName..."
    $fileList = $notebooks[$nbName]
    $cells = @()
    
    # Header
    $cells += @{
        "cell_type" = "markdown"
        "metadata"  = @{}
        "source"    = @("# Source Code Reference: $nbName")
    }

    foreach ($fileName in $fileList) {
        $path = Join-Path $srcDir $fileName
        if (Test-Path $path) {
            # Read raw content
            try {
                $content = Get-Content $path -Encoding UTF8 -Raw -ErrorAction Stop
            }
            catch {
                Write-Host "Error reading $fileName : $_"
                continue
            }
            
            # Split into lines. We want to preserve structure.
            # Simple line split
            $lines = $content -split "`r`n|`r|`n"
            
            # Add a trailing newline to each line for proper source format, though Jupyter handles lists fine.
            # We'll just pass the list of strings.
            
            # Add filename header
            $cells += @{
                "cell_type" = "markdown"
                "metadata"  = @{}
                "source"    = @("## $fileName")
            }
            
            # Add code cell
            $cells += @{
                "cell_type"       = "code"
                "execution_count" = $null
                "metadata"        = @{ "collapsed" = $true }
                "outputs"         = @()
                "source"          = $lines
            }
        }
        else {
            Write-Host "Warning: File not found: $fileName"
            # Add a placeholder
            $cells += @{
                "cell_type" = "markdown"
                "metadata"  = @{}
                "source"    = @("## $fileName (NOT FOUND)")
            }
        }
    }
    
    $nbContent = @{
        "cells"          = $cells
        "metadata"       = @{
            "kernelspec"    = @{
                "display_name" = "Python 3"
                "language"     = "python"
                "name"         = "python3"
            }
            "language_info" = @{
                "codemirror_mode"    = @{
                    "name"    = "ipython"
                    "version" = 3
                }
                "file_extension"     = ".py"
                "mimetype"           = "text/x-python"
                "name"               = "python"
                "nbconvert_exporter" = "python"
                "pygments_lexer"     = "ipython3"
                "version"            = "3.8.5"
            }
        }
        "nbformat"       = 4
        "nbformat_minor" = 4
    }
    
    # Convert to JSON with depth to handle the nested structure
    $json = $nbContent | ConvertTo-Json -Depth 100
    $outPath = Join-Path $outDir $nbName
    $json | Set-Content $outPath -Encoding UTF8
    Write-Host "Created $outPath"
}
