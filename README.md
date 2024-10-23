```
   ___ _ _     __       _                  _                 
  / _ (_) |_  / /  __ _| |__     /\  /\___| |_ __   ___ _ __ 
 / /_\/ | __|/ /  / _` | '_ \   / /_/ / _ \ | '_ \ / _ \ '__|
/ /_\\| | |_/ /__| (_| | |_) | / __  /  __/ | |_) |  __/ |   
\____/|_|\__\____/\__,_|_.__/  \/ /_/ \___|_| .__/ \___|_|   
                                            |_|              
```

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
4. Create a `gitlab_helper.ini` file with the following content:
    ```ini
    [gitlab]
    url = https://your-gitlab-url
    user = your-username
    private_token = your-private-token
    ```
5. Run the script using the following command:
    ```bash
    python glh.py
    ```
6. Use the command-line arguments to specify projects or groups to clone, or clone all:
    ```bash
    python glh.py --projects project1,project2
    python glh.py --groups group1,group2
    python glh.py --all
    ```

## License

This project is licensed under the GNU V3 License.