import os
import sys
import subprocess
import time
import shutil


def modify_algorithm_file(file_path, param_value):
    with open(file_path, "r") as file:
        content = file.read()
    modified_content = content.replace("TEST_SUBMISSION_PARAM", param_value)
    modified_file_path = f"modified_{os.path.basename(file_path)}"
    with open(modified_file_path, "w") as file:
        file.write(modified_content)
    return modified_file_path


def submit_algorithm(file_path, output_dir, prosperity_token):
    command = f"prosperity2submit --out {output_dir}/submission.log {file_path}"
    print("=" * 40)
    print(f"Running command: {command}")
    print("=" * 40)

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Send the token to the subprocess without waiting for the prompt
    process.stdin.write(prosperity_token + "\n")
    process.stdin.flush()

    # Read and print the output from the subprocess
    for line in process.stdout:
        print(line.strip())

    _, error = process.communicate()
    if process.returncode != 0:
        print("=" * 40)
        print(f"Error: {error.strip()}")
        print("=" * 40)
        sys.exit(1)


def find_latest_directory(base_dir):
    i = 0
    while True:
        directory = f"{base_dir}_{i}"
        if not os.path.exists(directory):
            return directory
        i += 1


def read_prosperity_token(token_file):
    with open(token_file, "r") as file:
        return file.read().strip()


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python script.py <algorithm_file> <token_file> <param_1> <param_2> ... <param_n>"
        )
        sys.exit(1)

    algorithm_file = sys.argv[1]
    token_file = sys.argv[2]
    param_values = sys.argv[3:]

    base_output_dir = "automated_test_value"
    latest_output_dir = find_latest_directory(base_output_dir)
    os.makedirs(latest_output_dir)

    prosperity_token = read_prosperity_token(token_file)

    for i, param_value in enumerate(param_values):
        print("=" * 40)
        print(f"Processing parameter value: {param_value}")
        print("=" * 40)
        modified_file_path = modify_algorithm_file(algorithm_file, param_value)
        output_dir = os.path.join(latest_output_dir, f"run_{i}")
        os.makedirs(output_dir)
        submit_algorithm(modified_file_path, output_dir, prosperity_token)
        os.remove(modified_file_path)
        time.sleep(5)  # Wait for a few seconds before the next submission

    print("=" * 40)
    print("All submissions completed.")
    print("=" * 40)


if __name__ == "__main__":
    main()
