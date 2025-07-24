# update-css.ps1

$cssLink = '<link rel="stylesheet" href="static/style_fournisseurs.css?v=3" type="text/css" />'

Get-ChildItem -Path ./templates -Filter *.html -Recurse | ForEach-Object {
    $path = $_.FullName
    $content = Get-Content $path -Raw

    # 1) Injecter le lien juste après <head> (si absent)
    if ($content -notmatch [regex]::Escape($cssLink)) {
        $content = $content -replace '(?i)<head>', "<head>`r`n    $cssLink"
    }

    # 2) Retirer les styles inline de couleur/background
    $content = $content -replace 'style="[^"]*(background:[^;"]+;?)[^"]*"', ''
    $content = $content -replace 'style="[^"]*(color:[^;"]+;?)[^"]*"', ''

    # 3) Sauvegarder
    Set-Content -Path $path -Value $content
}

Write-Host "Lien CSS injecté et couleurs inline supprimées dans tous les templates."
