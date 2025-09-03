$source = "Syllabus_plasma.pdf"
$destination = "1к_маг_E6_Фізика_плазми_(вибіркова)_Пономаренко_2025.pdf"

if (Test-Path $destination) {
    Remove-Item $destination -Force
}

Copy-Item -Path $source -Destination $destination