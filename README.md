# AWS S3 Prototype with LocalStack

## 1. What this project does

This project is a working prototype of **Amazon S3** (Simple Storage Service) that runs entirely on your own computer, using [LocalStack](https://github.com/localstack/localstack) in Docker. No real AWS account is needed and nothing is sent to AWS.

It demonstrates the basic S3 lifecycle, in two ways (AWS CLI in PowerShell, and Python with boto3):

1. Create a bucket
2. Upload a file (`notite.txt`)
3. List the objects in the bucket
4. Download the file under a different name and verify it matches the original (SHA256)
5. Delete the object
6. Delete the bucket (and confirm it is gone)

## 2. Prerequisites

| Tool | Notes | Version tested |
|---|---|---|
| Docker Desktop | Must be **running** before you start | 28.4.0 |
| AWS CLI v2 | Used by `demo.ps1` and the manual commands | 2.39.3 |
| Python 3 | On Windows, called through the `py` launcher | 3.14.0 |
| boto3 | Installed automatically from `requirements.txt` | 1.44.3 |

Tested on Windows 11 with Windows PowerShell 5.1.

Check your versions:

```powershell
docker --version
aws --version
py --version
```

Expected output (your versions may be newer):

```
Docker version 28.4.0, build d8eb465
aws-cli/2.39.3 Python/3.14.8 Windows/11 exe/AMD64
Python 3.14.0
```

> On Windows, the command `python` may not work before you create the virtual environment (it can open the Microsoft Store instead). Use `py`. After the virtual environment is activated, `python` works.

## 3. Project files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Starts LocalStack (S3 only) on `127.0.0.1:4566` |
| `demo.ps1` | PowerShell demo of all S3 operations using the AWS CLI |
| `s3_demo.py` | Python demo of the same operations using boto3 |
| `requirements.txt` | Python dependency (`boto3`, pinned version) |
| `notite.txt` | Sample file that is uploaded to S3 |
| `.gitignore` | Keeps generated files (`.venv/`, downloaded files) out of git |
| `README.md` | This documentation |

## 4. Start LocalStack

Clone the repository and enter the folder:

```powershell
git clone https://github.com/turculetandrei/aws-s3-localstack-demo.git
cd aws-s3-localstack-demo
```

Start LocalStack in the background:

```powershell
docker compose up -d
```

The first time, Docker downloads the `localstack/localstack:4.14` image (about 1.8 GB), so you will see many `Pulling` lines and it can take a few minutes. The output ends with:

```
 Container localstack-s3  Created
 Container localstack-s3  Starting
 Container localstack-s3  Started
```

Wait about 10 seconds, then check that the container is healthy:

```powershell
docker ps --format "{{.Names}} | {{.Image}} | {{.Status}} | {{.Ports}}"
```

Expected output:

```
localstack-s3 | localstack/localstack:4.14 | Up 12 seconds (healthy) | 127.0.0.1:4566->4566/tcp
```

Check that S3 is ready using the LocalStack health endpoint:

```powershell
$health = Invoke-RestMethod http://localhost:4566/_localstack/health
Write-Output "s3: $($health.services.s3) | edition: $($health.edition) | version: $($health.version)"
```

Expected output:

```
s3: available | edition: community | version: 4.14.0
```

(`available` changes to `running` after the first S3 request. Both mean S3 is ready.)

### Configuration

No `aws configure` is needed, and no file in `~/.aws` is created or changed. LocalStack accepts any credentials, so this project uses the fake values `test` / `test` and region `us-east-1`:

- `demo.ps1` sets them as environment variables for its own session only.
- `s3_demo.py` passes them directly to the boto3 client.
- For the manual commands (section 7), you set them in your terminal session.

Every command uses the endpoint `http://localhost:4566`, so nothing can reach real AWS.

## 5. Run the PowerShell demo

Run the script:

```powershell
.\demo.ps1
```

If PowerShell refuses to run scripts (see Troubleshooting), use this instead. It allows scripts only for this one run:

```powershell
powershell -ExecutionPolicy Bypass -File .\demo.ps1
```

Expected output (dates and transfer speeds will differ):

```
[1/8] Create bucket: capi-demo-bucket
{
    "Location": "/capi-demo-bucket",
    "BucketArn": "arn:aws:s3:::capi-demo-bucket"
}

[2/8] Upload notite.txt to s3://capi-demo-bucket/notite.txt
upload: .\notite.txt to s3://capi-demo-bucket/notite.txt

[3/8] List objects in s3://capi-demo-bucket
2026-11-16 10:37:20        272 notite.txt

[4/8] Download s3://capi-demo-bucket/notite.txt to notite_descarcat.txt
download: s3://capi-demo-bucket/notite.txt to .\notite_descarcat.txt

[5/8] Compare SHA256 of original vs downloaded
Original:   4229DF2C11E4B644BF8375FA0C2508EC0B8FE01E8400420534E36FF07BDF4C14
Downloaded: 4229DF2C11E4B644BF8375FA0C2508EC0B8FE01E8400420534E36FF07BDF4C14
MATCH

[6/8] Delete object s3://capi-demo-bucket/notite.txt
delete: s3://capi-demo-bucket/notite.txt

[7/8] Delete bucket: capi-demo-bucket

[8/8] List buckets (should be empty)
[]

Demo finished successfully.
```

Notes:

- During upload and download you may briefly see a progress line like `Completed 272 Bytes/272 Bytes (2.3 KiB/s) with 1 file(s) remaining`. It is replaced by the `upload:` / `download:` line. If you redirect the output to a file, both appear on the same line. This is normal.
- Step 7 prints nothing: `delete-bucket` produces no output when it succeeds.
- `[]` in step 8 means there are no buckets left.
- If any command fails, the script stops immediately with an error message.
- The script creates `notite_descarcat.txt` (ignored by git).

## 6. Run the Python demo

Create a virtual environment, activate it and install the dependency:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

After activation, your prompt starts with `(.venv)`. The install ends with:

```
Successfully installed boto3-1.44.3 botocore-1.44.3 jmespath-1.1.0 python-dateutil-2.9.0.post0 s3transfer-0.19.3 six-1.17.0 urllib3-2.8.0
```

Run the demo:

```powershell
python s3_demo.py
```

Expected output:

```
[1/8] Create bucket: capi-demo-bucket-py
Bucket created.

[2/8] Upload notite.txt to s3://capi-demo-bucket-py/notite.txt
Upload done.

[3/8] List objects in s3://capi-demo-bucket-py
notite.txt  272 bytes

[4/8] Download s3://capi-demo-bucket-py/notite.txt to notite_descarcat_py.txt
Download done.

[5/8] Compare SHA256 of original vs downloaded
Original:   4229DF2C11E4B644BF8375FA0C2508EC0B8FE01E8400420534E36FF07BDF4C14
Downloaded: 4229DF2C11E4B644BF8375FA0C2508EC0B8FE01E8400420534E36FF07BDF4C14
MATCH

[6/8] Delete object s3://capi-demo-bucket-py/notite.txt
Object deleted.

[7/8] Delete bucket: capi-demo-bucket-py
Bucket deleted.

[8/8] List buckets (should be empty)
[]
Confirmed: capi-demo-bucket-py is gone.

Demo finished successfully.
```

If LocalStack is not reachable, the script prints a message like the one below and exits with code 1:

```
ERROR: Could not connect to the endpoint URL: "http://localhost:4566/capi-demo-bucket-py"
```

The script creates `notite_descarcat_py.txt` (ignored by git).

## 7. Manual S3 commands

Run these one at a time to see each operation separately. (As in section 5, uploads and downloads may briefly show a `Completed ...` progress line first.)

First, set the fake credentials for the current PowerShell session (they disappear when you close the window):

```powershell
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

**Create a bucket**

```powershell
aws --endpoint-url http://localhost:4566 s3 mb s3://my-manual-bucket
```
```
make_bucket: my-manual-bucket
```

**List buckets**

```powershell
aws --endpoint-url http://localhost:4566 s3 ls
```
```
2026-11-16 10:49:00 my-manual-bucket
```

**Upload a file**

```powershell
aws --endpoint-url http://localhost:4566 s3 cp .\notite.txt s3://my-manual-bucket/notite.txt
```
```
upload: .\notite.txt to s3://my-manual-bucket/notite.txt
```

**List objects in the bucket**

```powershell
aws --endpoint-url http://localhost:4566 s3 ls s3://my-manual-bucket/
```
```
2026-11-16 10:49:03        272 notite.txt
```

**Download the file under a different name and read it**

```powershell
aws --endpoint-url http://localhost:4566 s3 cp s3://my-manual-bucket/notite.txt .\notite_descarcat.txt
Get-Content .\notite_descarcat.txt
```
```
download: s3://my-manual-bucket/notite.txt to .\notite_descarcat.txt
Amazon S3 (Simple Storage Service) este serviciul AWS pentru stocarea de obiecte.
Datele sunt pastrate ca obiecte in containere numite bucket-uri.
Fiecare obiect este identificat printr-o cheie (key) unica in bucket.
In acest proiect, S3 este simulat local cu LocalStack.
```

**Verify the download matches the original**

```powershell
(Get-FileHash .\notite.txt).Hash -eq (Get-FileHash .\notite_descarcat.txt).Hash
```
```
True
```

**Delete the object**

```powershell
aws --endpoint-url http://localhost:4566 s3 rm s3://my-manual-bucket/notite.txt
```
```
delete: s3://my-manual-bucket/notite.txt
```

**Delete the bucket** (a bucket must be empty before it can be deleted)

```powershell
aws --endpoint-url http://localhost:4566 s3 rb s3://my-manual-bucket
```
```
remove_bucket: my-manual-bucket
```

**Confirm it is gone**

```powershell
aws --endpoint-url http://localhost:4566 s3 ls
```

This prints nothing, because there are no buckets left.

## 8. Stop and clean up

If the virtual environment is active, leave it:

```powershell
deactivate
```

Stop and remove the LocalStack container:

```powershell
docker compose down
```

Expected output (the network name is based on your folder name):

```
 Container localstack-s3  Stopping
 Container localstack-s3  Stopped
 Container localstack-s3  Removing
 Container localstack-s3  Removed
 Network <folder-name>_default  Removing
 Network <folder-name>_default  Removed
```

All S3 data lives only inside the container, so it is gone after `docker compose down`.

Optionally, delete the generated local files:

```powershell
Remove-Item .\notite_descarcat.txt, .\notite_descarcat_py.txt -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\.venv
```

Optionally, remove the downloaded image to free disk space:

```powershell
docker rmi localstack/localstack:4.14
```

## 9. Troubleshooting

**Docker is not running**

`docker compose up -d` fails with an error about connecting to the Docker engine. Start Docker Desktop, wait until it says it is running, then check:

```powershell
docker info --format "{{.ServerVersion}}"
```

It should print a version number (for example `28.4.0`). Then run `docker compose up -d` again.

**LocalStack is not reachable**

The scripts fail with:

```
Could not connect to the endpoint URL: "http://localhost:4566/..."
```

The container is not running or not ready yet. Run `docker compose up -d`, wait about 10 seconds and check `docker ps` shows `(healthy)`.

**Port 4566 is already in use**

`docker compose up -d` fails because port 4566 is taken, often by another LocalStack container. See which containers use the port:

```powershell
docker ps --filter "publish=4566" --format "{{.Names}} | {{.Ports}}"
```

If it is another container, stop it with `docker stop <name>`. If no container is listed, find the program holding the port:

```powershell
Get-NetTCPConnection -LocalPort 4566 -ErrorAction SilentlyContinue | Select-Object LocalAddress, State, OwningProcess
Get-Process -Id <OwningProcess>
```

Close that program, or change the port in `docker-compose.yml` (for example `"127.0.0.1:4567:4566"`). If you change the port, also change `4566` in `demo.ps1`, `s3_demo.py` and the commands above.

**Script execution policy**

Running `.\demo.ps1` or `.\.venv\Scripts\Activate.ps1` fails with:

```
File ...\demo.ps1 cannot be loaded because running scripts is disabled on this system.
```

Either run the demo for this run only:

```powershell
powershell -ExecutionPolicy Bypass -File .\demo.ps1
```

or allow local scripts for your user (one time):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 10. Note about the pinned LocalStack image

`docker-compose.yml` uses `localstack/localstack:4.14` instead of `latest` on purpose. Since March 2026, newer LocalStack images require a LocalStack account and an auth token to start. Version 4.14 is the last one that runs without an account, so the project works out of the box for anyone who clones it.
