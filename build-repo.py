import subprocess
import os
import sys

# Define the build directory and repository names
BUILD_DIR = "build-dir"
REPO_DIR = "repo"
APP_JSON = "io.github.thorhent.CA.json"
GPG_KEY = "8C150BE1EFCF24B432ECA1D42BFB2B151EF7AB3D"

def run_command(command, description):
    """
    Runs a shell command and prints its status.
    
    Args:
        command (list): A list of strings representing the command and its arguments.
        description (str): A human-readable description of the command.
    """
    print(f"--- Running: {description} ---")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Success!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {description}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command not found. Make sure flatpak-builder is installed and in your PATH.")
        sys.exit(1)

def main():
    """Main function to execute the build process."""
    # Step 1: Remove the existing repository directory
    if os.path.exists(REPO_DIR):
        run_command(["rm", "-rf", REPO_DIR], f"Removing existing directory '{REPO_DIR}'")
    else:
        print(f"Directory '{REPO_DIR}' not found. Skipping removal.\n")

    # Step 2: Create a new repository directory
    run_command(["mkdir", REPO_DIR], f"Creating directory '{REPO_DIR}'")

    # Step 3: Run the flatpak-builder command
    flatpak_builder_cmd = [
        "flatpak-builder",
        "--force-clean",
        f"--repo={REPO_DIR}",
        f"--gpg-sign={GPG_KEY}",
        BUILD_DIR,
        APP_JSON
    ]
    run_command(flatpak_builder_cmd, "Running flatpak-builder")

    print("All commands executed successfully!")

if __name__ == "__main__":
    main()

