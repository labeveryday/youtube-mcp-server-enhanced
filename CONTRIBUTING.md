# Contributing to YouTube MCP Server Enhanced

Thank you for your interest in contributing to YouTube MCP Server Enhanced! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/youtube-mcp-server-enhanced.git
   cd youtube-mcp-server-enhanced
   ```

2. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make Your Changes**
   - Follow the existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests**
   ```bash
   pytest
   pytest --cov=youtube_mcp_server  # With coverage
   ```

4. **Format Code**
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

5. **Type Checking**
   ```bash
   mypy src/
   ```

6. **Commit and Push**
   ```bash
   git commit -m 'Add amazing feature'
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**

## Code Style

- **Python 3.10+** compatibility
- **Black** for code formatting
- **isort** for import sorting
- **Type hints** for all functions
- **Pydantic models** for data validation
- **Comprehensive docstrings** for public APIs

## Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use pytest fixtures for common test data
- Mock external dependencies (YouTube API calls)

## Documentation

- Update README.md for new features
- Add docstrings to all public functions
- Include usage examples for new tools
- Update type hints and schemas

## Pull Request Guidelines

- **Clear description** of changes
- **Reference related issues** if applicable
- **Include tests** for new functionality
- **Update documentation** as needed
- **Ensure CI passes** before requesting review

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow GitHub's community guidelines

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Contact the maintainer: duanlig@amazon.com

Thank you for contributing! 🚀
