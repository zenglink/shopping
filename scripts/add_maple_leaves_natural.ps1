param(
    [string]$InputPath = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

if ([string]::IsNullOrWhiteSpace($InputPath)) {
    $InputPath = Get-ChildItem -LiteralPath 'D:\Downloads' -Filter 'ChatGPT Image *14_59_32.png' |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}

if ([string]::IsNullOrWhiteSpace($InputPath) -or !(Test-Path -LiteralPath $InputPath)) {
    throw "Input image was not found."
}

$OutputDir = Join-Path (Get-Location) 'output'
$OutputPath = Join-Path $OutputDir 'coal-town-maple-more-natural.png'

if (!(Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

function Get-ClampedInt {
    param(
        [double]$Value,
        [int]$Min,
        [int]$Max
    )

    if ($Value -lt $Min) { return $Min }
    if ($Value -gt $Max) { return $Max }
    return [int][Math]::Round($Value)
}

function New-LeafStamp {
    param(
        [System.Drawing.Bitmap]$Source,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height
    )

    $stamp = [System.Drawing.Bitmap]::new($Width, $Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

    for ($yy = 0; $yy -lt $Height; $yy++) {
        for ($xx = 0; $xx -lt $Width; $xx++) {
            $c = $Source.GetPixel($X + $xx, $Y + $yy)
            $hue = $c.GetHue()
            $sat = $c.GetSaturation()
            $bright = $c.GetBrightness()

            $warmHue = (($hue -ge 5 -and $hue -le 65) -or $hue -ge 350)
            $warmEnough = (($c.R - $c.B) -gt 16 -and $c.R -gt 72 -and $c.G -gt $c.B)
            $notPaper = !($bright -gt 0.78 -and $sat -lt 0.34)

            $alpha = 0
            if ($warmHue -and $warmEnough -and $notPaper) {
                $alpha = (($sat - 0.10) / 0.38) * 235
                if ($bright -lt 0.48) {
                    $alpha = [Math]::Max($alpha, (($sat - 0.06) / 0.28) * 210)
                }
            }

            $a = Get-ClampedInt -Value $alpha -Min 0 -Max 235
            if ($a -lt 28) { $a = 0 }

            $stamp.SetPixel($xx, $yy, [System.Drawing.Color]::FromArgb($a, $c.R, $c.G, $c.B))
        }
    }

    return $stamp
}

function Draw-Stamp {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Bitmap]$Stamp,
        [double]$X,
        [double]$Y,
        [double]$Scale,
        [double]$Angle,
        [double]$Opacity
    )

    $state = $Graphics.Save()
    $Graphics.TranslateTransform([single]$X, [single]$Y)
    $Graphics.RotateTransform([single]$Angle)

    $w = [int][Math]::Round($Stamp.Width * $Scale)
    $h = [int][Math]::Round($Stamp.Height * $Scale)
    $dest = [System.Drawing.Rectangle]::new([int][Math]::Round(-$w / 2), [int][Math]::Round(-$h / 2), $w, $h)

    $matrix = [System.Drawing.Imaging.ColorMatrix]::new()
    $matrix.Matrix00 = 1
    $matrix.Matrix11 = 1
    $matrix.Matrix22 = 1
    $matrix.Matrix33 = [single]$Opacity
    $matrix.Matrix44 = 1

    $attrs = [System.Drawing.Imaging.ImageAttributes]::new()
    $attrs.SetColorMatrix($matrix, [System.Drawing.Imaging.ColorMatrixFlag]::Default, [System.Drawing.Imaging.ColorAdjustType]::Bitmap)

    $Graphics.DrawImage(
        $Stamp,
        $dest,
        0,
        0,
        $Stamp.Width,
        $Stamp.Height,
        [System.Drawing.GraphicsUnit]::Pixel,
        $attrs
    )

    $attrs.Dispose()
    $Graphics.Restore($state)
}

$image = [System.Drawing.Bitmap]::FromFile($InputPath)
$canvas = [System.Drawing.Bitmap]::new($image.Width, $image.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($canvas)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$g.DrawImage($image, 0, 0, $image.Width, $image.Height)

$stampTopLeft = New-LeafStamp -Source $image -X 0 -Y 0 -Width 88 -Height 98
$stampTopRight = New-LeafStamp -Source $image -X 845 -Y 0 -Width 209 -Height 112
$stampRightSmall = New-LeafStamp -Source $image -X 1010 -Y 895 -Width 44 -Height 112
$stampBottomRight = New-LeafStamp -Source $image -X 934 -Y 1354 -Width 120 -Height 138

$placements = @(
    # Strengthen the existing leafy canopy.
    @($stampTopLeft, 26, 18, 1.02, -8, 0.80),
    @($stampTopLeft, 103, 18, 0.48, 28, 0.48),
    @($stampTopRight, 914, 20, 0.88, 0, 0.72),
    @($stampTopRight, 1018, 68, 0.54, 26, 0.56),
    @($stampTopRight, 795, 17, 0.42, -30, 0.46),
    @($stampTopRight, 708, 19, 0.28, 20, 0.34),

    # Add side leaves, kept mostly outside the content blocks.
    @($stampTopLeft, -1, 138, 0.42, -54, 0.54),
    @($stampTopLeft, 8, 276, 0.37, -20, 0.48),
    @($stampTopLeft, 7, 438, 0.34, 34, 0.44),
    @($stampTopLeft, 8, 721, 0.35, -35, 0.46),
    @($stampTopLeft, 12, 974, 0.36, 24, 0.46),
    @($stampTopLeft, 12, 1288, 0.43, -22, 0.52),
    @($stampTopRight, 1050, 224, 0.28, 88, 0.40),
    @($stampTopRight, 1045, 383, 0.25, 132, 0.38),
    @($stampRightSmall, 1042, 520, 0.88, 8, 0.62),
    @($stampRightSmall, 1040, 812, 0.92, -18, 0.62),
    @($stampRightSmall, 1042, 1098, 0.84, 18, 0.54),
    @($stampBottomRight, 1032, 1272, 0.50, -22, 0.56),

    # Give the bottom edge a fuller autumn frame without covering labels.
    @($stampBottomRight, 985, 1419, 0.96, 0, 0.82),
    @($stampBottomRight, 1042, 1468, 0.76, 26, 0.70),
    @($stampTopRight, 825, 1487, 0.36, 176, 0.42),
    @($stampTopLeft, 650, 1486, 0.34, 154, 0.36),
    @($stampTopLeft, 505, 1484, 0.30, 188, 0.34),
    @($stampTopRight, 360, 1488, 0.34, 170, 0.36),
    @($stampTopLeft, 110, 1479, 0.54, 174, 0.54),
    @($stampTopLeft, 15, 1426, 0.48, 116, 0.58)
)

foreach ($p in $placements) {
    Draw-Stamp -Graphics $g -Stamp $p[0] -X $p[1] -Y $p[2] -Scale $p[3] -Angle $p[4] -Opacity $p[5]
}

$stampTopLeft.Dispose()
$stampTopRight.Dispose()
$stampRightSmall.Dispose()
$stampBottomRight.Dispose()

$canvas.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$image.Dispose()
$canvas.Dispose()

Write-Output $OutputPath
