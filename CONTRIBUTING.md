# Contributing

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this repository. 

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Handling Bugs](#handling-bugs)
- [Getting Started](#getting-started)
- [Commit Guidelines](#commit-guidelines)
- [Code Formatting](#code-formatting)
- [Merge Request Process](#merge-request-process)
- [License](#license)
- [Questions or Additional Help](#questions-or-additional-help)

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](./CONDUCT.md). By participating in this project you agree to abide by its terms. Please report unacceptable behavior to the project maintainers.

## Handling Bugs

If you find a bug, please report it by creating an issue in the GitLab Issue Tracker. If you are able to fix a bug, please fork the repository (if not a maintainer), create a new branch, apply your fix, and submit a merge request as outlined below.

## Getting Started

If you are not an active maintainer, please fork the official repository and clone the fork to your local machine. Active maintainers can create branches directly in the main repository.

## Commit Guidelines

This project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. Commit messages should be formatted according to this format:

```
<type>(<scope>): <short summary>
```

- **Type** (required): Indicates the purpose of the commit. Types include:
  - `build`: Changes that affect the build system or external dependencies
  - `ci`: Changes to CI configuration files and scripts
  - `chore`: Other changes that don't modify src or test files
  - `data`: Changes to data files
  - `docs`: Documentation only changes
  - `feat`: A new feature
  - `fix`: A bug fix
  - `perf`: A code change that improves performance
  - `refactor`: A code change that neither fixes a bug nor adds a feature
  - `test`: Adding missing tests or correcting existing tests

- **Scope** (optional): A specific aspect of the project affected by the change, such as `data-model`, `analytics`, or `visualization`.

- **Summary** (required): A brief description of the changes, written in the present tense, not capitalized, and without a period at the end.

## Code Formatting

Please run `make lint` before submitting a merge request to ensure your code adheres to the project's formatting standards. This command will run the linter and formatter for both Python and Snakemake files.

## Merge Request Process

1. **Make sure your branch is up to date** with the main branch.
2. **Create a merge request** on GitLab, set the `main` branch as the target.
3. **Ensure your merge request describes the changes** and link any relevant issues.
4. **Request a review** from at least one maintainer.
5. **After review, a maintainer can merge the request** if all criteria are met.

## License

This project is licensed under the [MIT License](./LICENSE). By contributing to this project, you agree that your contributions will be licensed under its terms.

## Questions or Additional Help

If you have any questions or require assistance, please use the GitLab Issue Tracker associated with this project. This is our preferred channel for communication regarding this project.
