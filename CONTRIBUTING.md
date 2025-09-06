# Contributing to AI Game Development Ecosystem

Thank you for your interest in contributing! This project aims to democratize game development through AI, and we welcome contributions from developers of all skill levels.

## 🚀 Quick Start

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ai-game-dev/ai-game-dev-ecosystem.git
   cd ai-game-dev-ecosystem
   ```

2. **Install UV (recommended)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up the workspace**
   ```bash
   uv sync --all-extras
   ```

4. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific package tests  
uv run pytest packages/ai_game_dev/tests/

# Run with coverage
uv run pytest --cov=packages --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black packages/
uv run ruff format packages/

# Lint code
uv run ruff check packages/

# Type checking
uv run mypy packages/
```

## 🏗️ Project Structure

```
packages/
├── ai_game_dev/           # Core LangGraph orchestration
├── ai_game_assets/        # Multimedia asset generation
├── pygame_game_dev/       # Pygame bindings
├── arcade_game_dev/       # Arcade bindings
├── bevy_game_dev/         # Rust Bevy bindings
└── godot_game_dev/        # Godot GDScript plugin

examples/                  # Example projects and tutorials
tests/                    # Integration tests
docs/                     # Documentation
.github/workflows/        # CI/CD pipelines
```

## 🤝 How to Contribute

### 1. Choose Your Contribution Type

**🐛 Bug Fixes**
- Look for issues labeled `bug` or `good first issue`
- Include test cases that reproduce the bug
- Ensure your fix doesn't break existing functionality

**✨ New Features**  
- Check existing issues or create a new feature request
- Discuss implementation approach before starting
- Include comprehensive tests and documentation

**📚 Documentation**
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify explanations

**🔧 Performance Improvements**
- Profile before and after changes
- Include benchmarks demonstrating improvements
- Consider backward compatibility

**🎮 Engine Support**
- Add support for new game engines
- Follow existing patterns in engine adapters
- Include example projects

### 2. Development Workflow

1. **Fork and Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow the coding standards below
   - Write tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   uv run pytest
   uv run mypy packages/
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add awesome new feature"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use the provided PR template
   - Link to related issues
   - Include screenshots/demos for UI changes

## 📋 Coding Standards

### Python Code Style

- **Formatting**: Use `black` and `ruff`
- **Type Hints**: All public functions must have type hints
- **Docstrings**: Use Google-style docstrings
- **Imports**: Use `isort` for import organization

```python
from typing import List, Dict, Any, Optional
import asyncio

async def generate_game_assets(
    descriptions: List[str], 
    style: str = "realistic"
) -> Dict[str, Any]:
    """Generate game assets from text descriptions.
    
    Args:
        descriptions: List of asset descriptions
        style: Visual style for generation
        
    Returns:
        Dictionary mapping asset names to generated content
        
    Raises:
        GenerationError: If asset generation fails
    """
    # Implementation here
    pass
```

### Rust Code Style

- **Formatting**: Use `cargo fmt`
- **Linting**: Use `cargo clippy`
- **Documentation**: Document all public APIs
- **Error Handling**: Use `Result<T, E>` for fallible operations

```rust
/// Generate a Bevy game project from specification
pub async fn generate_bevy_project(
    spec: &GameSpec
) -> Result<BevyProject, GenerationError> {
    // Implementation here
}
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(pygame): add particle system support
fix(assets): resolve audio generation timeout
docs: update getting started guide
```

## 🧪 Testing Guidelines

### Test Structure

```python
# tests/test_feature.py
import pytest
from ai_game_dev import FeatureClass

class TestFeature:
    """Test suite for Feature functionality."""
    
    @pytest.fixture
    def feature_instance(self):
        """Create feature instance for testing."""
        return FeatureClass()
    
    def test_basic_functionality(self, feature_instance):
        """Test basic feature operation."""
        result = feature_instance.do_something()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, feature_instance):
        """Test async feature operation."""
        result = await feature_instance.do_async_something()
        assert result is not None
```

### Test Categories

- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test package interactions  
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Benchmark critical paths

### Mock External Services

```python
@pytest.fixture
def mock_openai_client(monkeypatch):
    """Mock OpenAI API calls."""
    mock_response = {"choices": [{"text": "Generated content"}]}
    
    def mock_create(*args, **kwargs):
        return mock_response
    
    monkeypatch.setattr("openai.Completion.create", mock_create)
```

## 📖 Documentation Guidelines

### Code Documentation

- **Modules**: Include module-level docstring
- **Classes**: Document purpose and usage
- **Functions**: Document parameters, returns, and raises
- **Complex Logic**: Add inline comments

### User Documentation

- **Getting Started**: Help new users quickly succeed
- **API Reference**: Complete function/class documentation  
- **Examples**: Working code samples
- **Tutorials**: Step-by-step guides

### Documentation Format

Use Markdown with consistent formatting:

```markdown
## Section Title

Brief section description.

### Subsection

Content here.

```python
# Code example with syntax highlighting
from ai_game_dev import AIGameDev

game_dev = AIGameDev()
```

**Important**: Use callout boxes for important information.
```

## 🎯 Specific Contribution Areas

### AI/ML Improvements

- Enhance prompt engineering for better game generation
- Add support for new AI models and providers
- Improve content validation and safety
- Optimize inference performance

### Game Engine Integration

- Add support for Unity, Unreal, Construct 3
- Improve existing engine adapters
- Create engine-specific optimizations
- Build cross-engine compatibility tools

### Asset Generation

- Add support for 3D models, animations, shaders
- Improve audio generation quality
- Create style transfer capabilities
- Build asset preprocessing pipelines

### Developer Experience

- Improve error messages and debugging
- Add IDE extensions and plugins
- Create visual tools and GUIs
- Build CLI utilities

## 🌟 Recognition

Contributors are recognized in several ways:

- **README Contributors Section**: Listed in repository
- **Release Notes**: Mentioned in version releases  
- **Community Highlights**: Featured in blog posts
- **Maintainer Status**: Long-term contributors become maintainers

## 📞 Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Discord**: Real-time community chat
- **Office Hours**: Weekly community calls
- **Mentorship**: Pair with experienced contributors

## 🤔 Questions?

Feel free to reach out:

- Create a GitHub Discussion
- Join our Discord community
- Attend community office hours
- Email: contribute@ai-game-dev.org

Thank you for helping make game development more accessible through AI! 🚀