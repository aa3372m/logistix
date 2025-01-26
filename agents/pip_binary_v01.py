import json
import os
import subprocess
import shutil
import sys
from pathlib import Path

def process_request(request_file):
    # Read request
    with open(request_file, 'r') as f:
        request = json.load(f)

    # Get parameters
    params = request['parameters']
    package = params['package']
    platform = params['platform']
    python_version = params['python-version']

    # Get contract directory
    contract_dir = Path(request_file).parent
    package_dir = contract_dir / package

    # Create package directory
    package_dir.mkdir(exist_ok=True)

    try:
        # Download package
        cmd = [
            'pip', 'download',
            '--platform', platform,
            '--only-binary=:all:',
            f'--python-version={python_version}',
            '-d', str(package_dir),
            package
        ]
        subprocess.run(cmd, check=True)

        # Create zip file
        zip_path = contract_dir / f'{package}.zip'
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', package_dir)

        # Create response
        response = {
            "key": request['key'],
            "contractcode": request['contractcode'],
            "agent": request['agent'],
            "status": "done",
            "parameters": params,
            "output": f"Package {package} has been downloaded and zipped successfully"
        }

    except Exception as e:
        response = {
            "key": request['key'],
            "contractcode": request['contractcode'],
            "agent": request['agent'],
            "status": "error",
            "parameters": params,
            "error": str(e)
        }

    # Save response
    with open(contract_dir / 'response.json', 'w') as f:
        json.dump(response, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pip_binary_v01.py <request_file>")
        sys.exit(1)

    process_request(sys.argv[1]) 