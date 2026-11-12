# Збірка PlasmaBook: lualatex + biber через latexmk (див. шапку main.tex).
# Використання:  .\build.ps1          — зібрати main.pdf
#                .\build.ps1 -Clean   — спершу прибрати допоміжні файли
param([switch]$Clean)

Set-Location $PSScriptRoot

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
