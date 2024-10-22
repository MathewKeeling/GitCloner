# GitCloner

This repository contains the `git_cloner.py` file, which is a Python script for cloning GitLab repositories.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Git installed

## Usage

To use the `git_cloner.py` script, follow these steps:

1. Clone this repository to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the cloned repository directory.
4. Create a `gitcloner.ini` file with the following content:
    ```ini
    [gitlab]
    url = https://your-gitlab-url
    user = your-username
    private_token = your-private-token
    ```
5. Run the script using the following command:
    ```bash
    python git_cloner.py
    ```
6. Use the command-line arguments to specify projects or groups to clone, or clone all:
    ```bash
    python git_cloner.py --projects project1,project2
    python git_cloner.py --groups group1,group2
    python git_cloner.py --all
    ```

## License

This project is licensed under the GNU V3 License.
