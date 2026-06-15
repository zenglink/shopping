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
$OutputPath = Join-Path $OutputDir 'coal-town-maple-more.png'

if (!(Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

function New-MapleLeafPath {
    param(
        [double]$Size
    )

    $points = @(
        @(0.00, -1.00),
        @(0.13, -0.54),
        @(0.42, -0.82),
        @(0.35, -0.39),
        @(0.78, -0.46),
        @(0.47, -0.17),
        @(0.95, 0.05),
        @(0.45, 0.09),
        @(0.58, 0.45),
        @(0.20, 0.25),
        @(0.06, 0.92),
        @(0.00, 0.38),
        @(-0.06, 0.92),
        @(-0.20, 0.25),
        @(-0.58, 0.45),
        @(-0.45, 0.09),
        @(-0.95, 0.05),
        @(-0.47, -0.17),
        @(-0.78, -0.46),
        @(-0.35, -0.39),
        @(-0.42, -0.82),
        @(-0.13, -0.54)
    )

    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $scaled = New-Object 'System.Drawing.PointF[]' $points.Count
    for ($i = 0; $i -lt $points.Count; $i++) {
        $scaled[$i] = [System.Drawing.PointF]::new(
            [single]($points[$i][0] * $Size * 0.5),
            [single]($points[$i][1] * $Size * 0.5)
        )
    }
    $path.AddPolygon($scaled)
    return $path
}

function Draw-Leaf {
    param(
        [System.Drawing.Graphics]$Graphics,
        [double]$X,
        [double]$Y,
        [double]$Size,
        [double]$Angle,
        [System.Drawing.Color]$Color,
        [int]$Alpha
    )

    $state = $Graphics.Save()
    $Graphics.TranslateTransform([single]$X, [single]$Y)
    $Graphics.RotateTransform([single]$Angle)

    $path = New-MapleLeafPath -Size $Size
    $fillColor = [System.Drawing.Color]::FromArgb($Alpha, $Color.R, $Color.G, $Color.B)
    $lineColor = [System.Drawing.Color]::FromArgb([Math]::Min(220, $Alpha + 25), [Math]::Max(0, $Color.R - 42), [Math]::Max(0, $Color.G - 34), [Math]::Max(0, $Color.B - 24))
    $brush = [System.Drawing.SolidBrush]::new($fillColor)
    $pen = [System.Drawing.Pen]::new($lineColor, [single]([Math]::Max(0.7, $Size / 34)))

    $Graphics.FillPath($brush, $path)
    $Graphics.DrawPath($pen, $path)

    $veinPen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb([Math]::Min(190, $Alpha), [Math]::Max(0, $Color.R - 56), [Math]::Max(0, $Color.G - 44), [Math]::Max(0, $Color.B - 32)), [single]([Math]::Max(0.5, $Size / 55)))
    $tips = @(
        @(0.00, -0.48),
        @(0.40, -0.22),
        @(0.47, 0.03),
        @(0.15, 0.24),
        @(-0.15, 0.24),
        @(-0.47, 0.03),
        @(-0.40, -0.22)
    )
    foreach ($tip in $tips) {
        $Graphics.DrawLine(
            $veinPen,
            [single]0,
            [single]($Size * 0.18),
            [single]($tip[0] * $Size),
            [single]($tip[1] * $Size)
        )
    }
    $Graphics.DrawLine($veinPen, [single]0, [single]($Size * 0.28), [single]0, [single]($Size * 0.55))

    $veinPen.Dispose()
    $pen.Dispose()
    $brush.Dispose()
    $path.Dispose()
    $Graphics.Restore($state)
}

$image = [System.Drawing.Bitmap]::FromFile($InputPath)
$canvas = [System.Drawing.Bitmap]::new($image.Width, $image.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($canvas)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.DrawImage($image, 0, 0, $image.Width, $image.Height)

$palette = @(
    [System.Drawing.Color]::FromArgb(177, 88, 26),
    [System.Drawing.Color]::FromArgb(198, 124, 42),
    [System.Drawing.Color]::FromArgb(216, 150, 58),
    [System.Drawing.Color]::FromArgb(143, 74, 30),
    [System.Drawing.Color]::FromArgb(226, 172, 82)
)

$leaves = @(
    # Top edge cluster, richer but kept above the title line.
    @(32, 14, 62, -26, 0, 188),
    @(86, 28, 42, 21, 2, 158),
    @(156, 17, 34, -44, 3, 128),
    @(253, 19, 26, 38, 4, 105),
    @(423, 20, 24, -18, 1, 92),
    @(666, 22, 28, 20, 4, 102),
    @(775, 24, 35, -36, 2, 126),
    @(882, 15, 52, 28, 1, 174),
    @(955, 21, 64, -18, 0, 196),
    @(1026, 51, 48, 39, 2, 164),
    # Left margin.
    @(9, 103, 34, 48, 1, 138),
    @(24, 178, 30, -28, 4, 112),
    @(11, 282, 32, 22, 2, 122),
    @(24, 432, 28, -42, 0, 104),
    @(12, 603, 34, 38, 3, 126),
    @(22, 773, 30, -20, 1, 114),
    @(15, 958, 33, 36, 4, 126),
    @(30, 1131, 30, -36, 2, 118),
    @(11, 1324, 40, 24, 0, 146),
    @(63, 1452, 45, -18, 1, 150),
    # Right margin.
    @(1044, 119, 35, -42, 1, 138),
    @(1029, 206, 31, 30, 4, 118),
    @(1041, 361, 29, -24, 2, 108),
    @(1029, 507, 34, 42, 0, 130),
    @(1045, 683, 31, -34, 1, 118),
    @(1027, 843, 40, 23, 2, 150),
    @(1039, 1023, 34, -38, 3, 132),
    @(1022, 1211, 37, 34, 4, 136),
    @(996, 1397, 50, -22, 0, 170),
    @(1030, 1456, 43, 18, 2, 150),
    # Bottom edge, mostly tucked outside the content line.
    @(129, 1482, 39, 26, 2, 134),
    @(257, 1468, 31, -18, 4, 104),
    @(382, 1478, 34, 32, 1, 118),
    @(512, 1473, 28, -30, 3, 98),
    @(644, 1479, 35, 18, 0, 126),
    @(768, 1465, 30, -24, 2, 108),
    @(902, 1481, 40, 28, 1, 136),
    # Soft inner accents in safe blank-ish areas.
    @(724, 76, 24, 31, 4, 82),
    @(832, 328, 25, -28, 2, 90),
    @(984, 402, 22, 24, 1, 78),
    @(940, 985, 24, 36, 3, 86),
    @(71, 648, 22, -25, 4, 78),
    @(52, 1041, 23, 28, 2, 80)
)

foreach ($leaf in $leaves) {
    $color = $palette[$leaf[4]]
    Draw-Leaf -Graphics $g -X $leaf[0] -Y $leaf[1] -Size $leaf[2] -Angle $leaf[3] -Color $color -Alpha $leaf[5]
}

# A very light warm paper haze over the added leaves ties them to the printed poster texture.
$haze = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(18, 244, 228, 194))
$g.FillRectangle($haze, 0, 0, $canvas.Width, $canvas.Height)
$haze.Dispose()

$encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/png' }
$params = [System.Drawing.Imaging.EncoderParameters]::new(1)
$params.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new([System.Drawing.Imaging.Encoder]::ColorDepth, 32L)
$canvas.Save($OutputPath, $encoder, $params)

$g.Dispose()
$image.Dispose()
$canvas.Dispose()

Write-Output $OutputPath
