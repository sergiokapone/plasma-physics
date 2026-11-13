# Збірка PlasmaBook: lualatex + biber через latexmk (див. шапку main.tex).
# Використання:  .\build.ps1                      — зібрати всю книгу (main.pdf)
#                .\build.ps1 -Clean               — спершу прибрати допоміжні файли
#                .\build.ps1 -Chapter Collisions  — зібрати ЛИШЕ один розділ -> _chapters\Collisions.pdf
#                                                   (через test.tex; посилання на інші розділи лишаються «??»;
#                                                   main.pdf і журнали книги не чіпає)
param([switch]$Clean, [string]$Chapter)

Set-Location $PSScriptRoot

if ($Chapter) {
    $src = Join-Path $PSScriptRoot "$Chapter\$Chapter.tex"
    if (-not (Test-Path $src)) {
        $all = (Get-ChildItem -Directory | Where-Object { Test-Path "$($_.FullName)\$($_.Name).tex" } | ForEach-Object Name) -join ', '
        "Немає $Chapter\$Chapter.tex. Розділи: $all"
        exit 1
    }
    $out = Join-Path $PSScriptRoot '_chapters'
    New-Item -ItemType Directory -Force "$out\$Chapter" | Out-Null
    $pretex = "\def\TargetChapter{$Chapter}"
    # розділ цитує джерела — надрукувати його літературу після тексту (перевірка посилань)
    $text = (Get-Content $src -Raw -Encoding UTF8) -replace '(?m)(?<!\\)%.*$', ''
    if ($text -match '\\(no)?cite') { $pretex += '\def\TargetBib{}' }
    $idx = 'upmendex -s "' + ((Join-Path $PSScriptRoot 'index-uk.ist') -replace '\\', '/') + '" %O -o %D %S'
    $lua = 'lualatex --shell-escape -interaction=nonstopmode -halt-on-error -file-line-error %O %P'
    latexmk -pdflua "-pretex=$pretex" "-lualatex=$lua" -e "`$makeindex = q($idx)" "-jobname=$Chapter" "-outdir=$out" test.tex | Out-Null
    $code = $LASTEXITCODE
    $log = "$out\$Chapter.log"
    if ($code -ne 0) {
        "Збірка не вдалась (код $code). Журнал: $log"
        Select-String -Path $log -Pattern '^!|:\d+: ' | Select-Object -First 8 | ForEach-Object { $_.Line }
    } else {
        "PDF: _chapters\$Chapter.pdf"
        $ov = @(Select-String -Path $log -Pattern '^(Overfull|Underfull) \\[hv]box')
        "Overfull/Underfull: $($ov.Count)"
        $ov | Select-Object -First 15 | ForEach-Object { $_.Line }
        if (Get-Command texlogsieve -ErrorAction SilentlyContinue) {
            texlogsieve --no-color --no-heartbeat --tips --box-detail $log > "$out\$Chapter-sieve.txt" 2>&1
            "Зведення по сторінках: _chapters\$Chapter-sieve.txt"
        }
    }
    exit $code
}

if ($Clean) { latexmk -C main.tex | Out-Null }

latexmk -lualatex -interaction=nonstopmode -file-line-error main.tex | Out-Null
$code = $LASTEXITCODE

# Короткий підсумок із main.log
$errs = Select-String -Path main.log -Pattern '^(\./)?[^ ]+:\d+:|^!' | Select-Object -First 15
if ($errs) { "--- Помилки ---"; $errs | ForEach-Object { $_.Line } }
$ref = Select-String -Path main.log -Pattern 'undefined (references|citations)|Reference .* undefined|Citation .* undefined' | Select-Object -First 10
if ($ref) { "--- Невизначені посилання ---"; $ref | ForEach-Object { $_.Line } }
$ov = (Select-String -Path main.log -Pattern '^Overfull \\hbox').Count
"Overfull hbox: $ov"

# Зведення texlogsieve (по сторінках, з порадами) -> sieve.txt; агент-верстальник читає цей файл
if (Get-Command texlogsieve -ErrorAction SilentlyContinue) {
    texlogsieve --no-color --no-heartbeat --tips --box-detail main.log > sieve.txt 2>&1
    $pg = Select-String -Path sieve.txt -Pattern '^pg \d+: (Overfull|Underfull)' -Encoding utf8
    "texlogsieve: $($pg.Count) over/underfull boxes; full report in sieve.txt"
}
"latexmk exit code: $code"
exit $code
