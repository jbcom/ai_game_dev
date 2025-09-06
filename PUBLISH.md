# Registry Publication Guide

This document outlines the steps to publish packages to official registries.

## 🐍 PyPI Publication (Python Packages)

### Prerequisites
```bash
# Install publishing tools
uv add --dev twine build

# Set up PyPI credentials
# Create ~/.pypirc with your API token
```

### Publishing Steps

1. **Build packages**
   ```bash
   cd packages/ai_game_dev && uv build --wheel
   cd ../ai_game_assets && uv build --wheel  
   cd ../pygame_game_dev && uv build --wheel
   cd ../arcade_game_dev && uv build --wheel
   ```

2. **Test on TestPyPI first**
   ```bash
   twine upload --repository testpypi dist/*.whl
   ```

3. **Publish to PyPI**
   ```bash
   twine upload dist/*.whl
   ```

### Installation Commands (after publishing)
```bash
pip install ai-game-dev
pip install ai-game-assets
pip install pygame-ai-game-dev
pip install arcade-ai-game-dev
```

## 🦀 Cargo/crates.io Publication (Rust)

### Prerequisites
```bash
# Install cargo and login
cargo install cargo-edit
cargo login <your-api-token>
```

### Publishing Steps

1. **Verify package**
   ```bash
   cd packages/bevy_game_dev
   cargo check
   cargo test
   ```

2. **Publish to crates.io**
   ```bash
   cargo publish
   ```

### Installation Command (after publishing)
```toml
[dependencies]
bevy-ai-game-dev = "1.0.0"
```

## 🎮 Godot Asset Library

### Prerequisites
- Godot Asset Library account
- Package following Godot plugin structure

### Publishing Steps

1. **Prepare submission**
   - Ensure plugin.cfg is properly configured
   - Create preview images and documentation
   - Test plugin in Godot editor

2. **Submit to Asset Library**
   - Visit https://godotengine.org/asset-library/
   - Upload package with metadata
   - Include screenshots and description

### Installation (after approval)
- Search "AI Game Development Generator" in Godot Asset Library
- Install directly from Godot editor

## 📋 Release Checklist

### Pre-Release
- [ ] All tests pass in CI
- [ ] Documentation is up to date
- [ ] Version numbers are bumped
- [ ] CHANGELOG.md is updated
- [ ] Examples work with new version
- [ ] Security audit completed

### Release Process
- [ ] Create GitHub release with tags
- [ ] Publish to PyPI
- [ ] Publish to crates.io
- [ ] Submit to Godot Asset Library
- [ ] Update documentation sites
- [ ] Announce on community channels

### Post-Release
- [ ] Monitor for issues
- [ ] Update installation guides
- [ ] Create release blog post
- [ ] Plan next version features

## 🏷️ Version Management

### Semantic Versioning
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Coordination
All packages should maintain compatible versions:
- Core packages (ai_game_dev, ai_game_assets): Same version
- Engine packages: Compatible version range
- Examples: Updated with each release

## 📊 Registry Analytics

### PyPI Downloads
Monitor package popularity:
```bash
# Install pypistats
pip install pypistats

# Check download stats
pypistats recent ai-game-dev
```

### Crates.io Downloads
- View stats at https://crates.io/crates/bevy-ai-game-dev
- Monitor in cargo registry dashboard

### Community Metrics
- GitHub stars and forks
- Documentation page views
- Community forum activity
- Discord member count

## 🚨 Emergency Procedures

### Yanking Releases
If critical issues are discovered:

**PyPI:**
```bash
twine yank <package> <version>
```

**Crates.io:**
```bash
cargo yank --vers <version>
```

### Security Issues
1. Create private security advisory on GitHub
2. Coordinate fix with maintainers
3. Prepare security release
4. Disclose responsibly after fix

## 📞 Registry Support

### PyPI Issues
- Email: admin@pypi.org
- Documentation: https://packaging.python.org/

### Crates.io Issues  
- GitHub: https://github.com/rust-lang/crates.io
- Discord: #crates-io on Rust Discord

### Godot Asset Library
- GitHub: https://github.com/godotengine/asset-library
- Forum: https://forum.godotengine.org/