# Changelog

## [2024.10.1] - 2024-10-23

### Added
- Introduced `--add_url` argument to add a new configuration section for a fully qualified domain name (FQDN).
- Introduced `--set_url` argument to set the selected GitLab URL.
- Introduced `--list_url` argument to list all available URLs in the configuration file.
- Improved user messages to be clearer and more informative.
- Configuration file path is now printed whenever the user needs to modify the INI file.
- Added validation for the `--set_url` argument to ensure the section exists before setting it.

### Changed
- The script now dynamically selects the appropriate configuration based on the selected GitLab URL.
- The script now instructs the user to update the INI file with relevant information when adding a new FQDN.

## [2024.10.0] - 2024-10-22

### Added
- Initial release of the script with the following features:
  - Cloning and updating GitLab repositories.
  - Command-line arguments for specifying projects, groups, or all repositories to clone.
  - Verbose logging option.
  - Creation of a configuration file with generic values if it does not exist.
  - Default user prompts for cloning repositories if no arguments are provided.
