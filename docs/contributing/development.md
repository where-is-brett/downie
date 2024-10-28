# Development Guide

This guide helps you set up your development environment for contributing to Downie.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg
- Git
- pip and virtualenv

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/where-is-brett/downie.git
cd downie
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev,docs]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

### Project Structure

```
downie/
├── src/
│   └── downie/
│       ├── cli/          # Command-line interface
│       ├── core/         # Core functionality
│       ├── models/       # Data models
│       └── utils/        # Utility functions
├── tests/               # Test files
├── docs/                # Documentation
├── examples/            # Example scripts
└── tools/               # Development tools
```

## Development Workflow

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and write tests

3. Run tests:
```bash
pytest
```

4. Run linting:
```bash
black .
isort .
flake8
mypy src/
```

5. Build documentation:
```bash
mkdocs serve
```

6. Commit changes:
```bash
git add .
git commit -m "Description of changes"
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_downloader.py

# Run with coverage
pytest --cov=downie

# Run marked tests
pytest -m "slow"
```

### Writing Tests

```python
import pytest
from downie.core.downloader import VideoDownloader

def test_download_success():
    """Test successful video download."""
    config = ...
    downloader = VideoDownloader(config)
    result = downloader.download()
    assert result.success
    assert result.filepath.exists()

@pytest.mark.slow
def test_large_download():
    """Test downloading large video."""
    ...

@pytest.fixture
def sample_video(tmp_path):
    """Create sample video for testing."""
    ...
```

## Documentation

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Writing Documentation

- Use Google-style docstrings
- Include examples in docstrings
- Add type hints
- Update relevant documentation files

### Example Docstring

```python
def process_video(self, input_path: Path) -> Path:
    """
    Process video according to configuration.
    
    Args:
        input_path: Path to input video file
        
    Returns:
        Path to processed video file
        
    Raises:
        ProcessingError: If processing fails
        
    Example:
        >>> processor = VideoProcessor(config)
        >>> output = processor.process_video('input.mp4')
    """
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run tests and build documentation
5. Create GitHub release
6. Deploy to PyPI

## Development Tools

### Required Tools

- black: Code formatting
- isort: Import sorting
- flake8: Linting
- mypy: Type checking
- pytest: Testing
- mkdocs: Documentation
- pre-commit: Git hooks

### Optional Tools

- pytest-cov: Coverage reporting
- pytest-xdist: Parallel testing
- pytest-watch: Test auto-running

## Debugging

### Using debugger:

```python
import pdb

def problematic_function():
    x = calculate_something()
    pdb.set_trace()  # Debugger will stop here
    process_result(x)
```

### Using logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
```

## Best Practices

1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Write descriptive docstrings
   - Keep functions focused

2. **Testing**
   - Write tests for new features
   - Maintain test coverage
   - Use appropriate fixtures
   - Mock external services

3. **Documentation**
   - Update docs with changes
   - Include examples
   - Explain complex features
   - Keep README updated

4. **Git Workflow**
   - Write clear commit messages
   - Keep commits focused
   - Rebase before merging
   - Use meaningful branch names

## Getting Help

- Check existing issues
- Join discussions
- Ask questions in pull requests
- Update documentation

## Next Steps

- Review [Code Style Guide](code-style.md)
- Check [Testing Guide](testing.md)