$ErrorActionPreference = "Stop"

$env:AWS_ACCESS_KEY_ID     = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION    = "us-east-1"
$env:AWS_PAGER             = ""

$Endpoint   = "http://localhost:4566"
$Bucket     = "capi-demo-bucket"
$Key        = "notite.txt"
$Original   = Join-Path $PSScriptRoot "notite.txt"
$Downloaded = Join-Path $PSScriptRoot "notite_descarcat.txt"

function Invoke-Aws {
    aws --endpoint-url $Endpoint @args
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI command failed (exit code $LASTEXITCODE): aws $($args -join ' ')"
    }
}

Write-Host "`n[1/8] Create bucket: $Bucket" -ForegroundColor Cyan
Invoke-Aws s3api create-bucket --bucket $Bucket

Write-Host "`n[2/8] Upload notite.txt to s3://$Bucket/$Key" -ForegroundColor Cyan
Invoke-Aws s3 cp $Original "s3://$Bucket/$Key"

Write-Host "`n[3/8] List objects in s3://$Bucket" -ForegroundColor Cyan
Invoke-Aws s3 ls "s3://$Bucket/"

Write-Host "`n[4/8] Download s3://$Bucket/$Key to notite_descarcat.txt" -ForegroundColor Cyan
Invoke-Aws s3 cp "s3://$Bucket/$Key" $Downloaded

Write-Host "`n[5/8] Compare SHA256 of original vs downloaded" -ForegroundColor Cyan
$HashOriginal   = (Get-FileHash $Original -Algorithm SHA256).Hash
$HashDownloaded = (Get-FileHash $Downloaded -Algorithm SHA256).Hash
Write-Host "Original:   $HashOriginal"
Write-Host "Downloaded: $HashDownloaded"
if ($HashOriginal -eq $HashDownloaded) {
    Write-Host "MATCH" -ForegroundColor Green
} else {
    Write-Host "MISMATCH" -ForegroundColor Red
    throw "Downloaded file does not match the original."
}

Write-Host "`n[6/8] Delete object s3://$Bucket/$Key" -ForegroundColor Cyan
Invoke-Aws s3 rm "s3://$Bucket/$Key"

Write-Host "`n[7/8] Delete bucket: $Bucket" -ForegroundColor Cyan
Invoke-Aws s3api delete-bucket --bucket $Bucket

Write-Host "`n[8/8] List buckets (should be empty)" -ForegroundColor Cyan
Invoke-Aws s3api list-buckets --query "Buckets[].Name"

Write-Host "`nDemo finished successfully." -ForegroundColor Green
