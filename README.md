```

```


<div align="center">

<table>
  <tr>
    <td>
      <pre>
   ___ _ _     __       _                  _                 
  / _ (_) |_  / /  __ _| |__     /\  /\___| |_ __   ___ _ __ 
 / /_\/ | __|/ /  / _` | '_ \   / /_/ / _ \ | '_ \ / _ \ '__|
/ /_\\| | |_/ /__| (_| | |_) | / __  /  __/ | |_) |  __/ |   
\____/|_|\__\____/\__,_|_.__/  \/ /_/ \___|_| .__/ \___|_|   
                                            |_|              
                                                  v2024.10.29
      </pre>
    </td>
    <td>
      <img src="glh.png" alt="Gitlab Helper" style="width: 200px; height: auto;">
    </td>
  </tr>
</table>

</div>

## Overview

This repository contains the `glh.py` file, a versatile Python script designed to streamline the process of managing GitLab repositories.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Git installed

## Usage

To use the `glh.py` script, follow these steps:

1. Clone this repository to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the cloned repository directory.
4. Create a `glh.ini` file with the following content:
    ```ini
    [gitlab]
    url = https://your-gitlab-url
    user = your-username
    private_token = your-private-token
    ```
5. Run the script using the following command:
    ```bash
    ./glh.sh
    ```
6. Use the command-line arguments to specify projects or groups to clone, or clone all:
    ```bash
    ./glh.sh --projects project1,project2
    ./glh.sh --groups group1,group2
    ./glh.sh --all
    ```

## Adding to Bin Directory

To use the `glh.sh` script from anywhere on your system, you can add it to your `bin` directory:

1. Move both the shell script and the Python script to your `bin` directory:
    ```bash
    mv glh.sh /usr/local/bin/glh
    mv glh.py /usr/local/bin/glh.py
    ```
2. Make sure the scripts are executable:
    ```bash
    chmod +x /usr/local/bin/glh
    chmod +x /usr/local/bin/glh.py
    ```
3. Now you can run the script from anywhere using:
    ```bash
    glh --projects project1,project2
    ```

## Configuration File Location

The script expects the configuration file to be located at `~/.glh/glh.ini` on Linux and other Unix-like systems, or `~\\.glh\\glh.ini` on Windows. If the configuration file does not exist, the script will create one with generic values and prompt you to update it.

## Performing Updates

To update the `glh.py` script and the wrapper:

1. Navigate to the cloned repository directory:
    ```bash
    cd /path/to/cloned/repository
    ```
2. Pull the latest changes from the repository:
    ```bash
    git pull origin main
    ```
3. If there are updates to the wrapper script, move both scripts to your `bin` directory again:
    ```bash
    mv glh.sh /usr/local/bin/glh
    mv glh.py /usr/local/bin/glh.py
    chmod +x /usr/local/bin/glh
    chmod +x /usr/local/bin/glh.py
    ```

## Supported Platforms

This script supports both Windows and Linux systems.

## Limitations

This script does **not** work with GitHub, and there are no plans to support GitHub.

*I'm not opposed to it, but because GitHub is not FOSS, I'm not very interested in building tooling for that. If you're viewing this project on GitHub: this repository is only a mirror. Forks and Pull Requests are welcomed! GPLv3 attribution(s) required where applicable.*

## License

This project is licensed under the GPLv3 License.
