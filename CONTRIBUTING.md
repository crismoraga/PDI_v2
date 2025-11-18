# Contributing to ZDex

Thank you for considering contributing to ZDex. This file outlines our code of conduct and contribution workflow.

## Contribution process

- Fork the repository
- Create a feature branch
- Follow the code style and add tests for new functionality
- Open a Pull Request (PR) and reference any relevant issue
- PRs should be small and reviewable

## Testing

- `pytest -q` should pass locally
- Add unit tests for any new behavior

## Code Style

- Use consistent type hints
- Use logging with `logger` object, not print

## Security

- Avoid committing model weights or secrets
- Do not add credentials in `.env` files
