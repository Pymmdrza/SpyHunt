# GitHub Actions & Automation

This directory contains GitHub Actions workflows and automation scripts for CI/CD.

## 📁 Contents

- **`bump_version.py`** - Automated version bumping script
- **`VERSION_BUMP_USAGE.txt`** - Quick reference for version commands
- **`hooks/`** - Git hooks for version consistency checks
- **`workflows/`** - GitHub Actions workflow definitions

## 🔄 Version Management

### Quick Start

```bash
# Bump version (from project root)
python .github/bump_version.py patch    # 4.0.0 → 4.0.1
python .github/bump_version.py minor    # 4.0.0 → 4.1.0
python .github/bump_version.py major    # 4.0.0 → 5.0.0

# Or from .github directory
cd .github
python bump_version.py patch
```

See `VERSION_BUMP_USAGE.txt` for complete documentation.

## Workflows

### 1. `test-build.yml` - Automated Testing

**Triggers:**
- Push to main/master/develop branches
- Pull requests
- Manual trigger

**What it does:**
- Tests building on Ubuntu, Windows, and macOS
- Tests with Python 3.7, 3.8, 3.9, 3.10, 3.11
- Verifies package integrity
- Tests installation
- Tests command availability

### 2. `manual-version-bump.yml` - Manual Version Bumping

**Triggers:**
- Manual: Via Actions tab

**What it does:**
- Bumps version (patch/minor/major)
- Updates all version files
- Commits and pushes changes
- Creates Git tag
- Generates changelog
- Creates GitHub Release

### 3. `auto-version-bump.yml` - Automatic Version Bumping

**Triggers:**
- Push to main/master branch

**What it does:**
- Detects bump type from commit messages
- Auto-bumps version accordingly
- Creates release automatically
- Skips with `[skip version]` in commit

### 4. `publish-to-pypi.yml` - Automated Deployment

**Triggers:**
- Automatic: When a GitHub release is published
- Manual: Via Actions tab (select TestPyPI or PyPI)

**What it does:**
- Verifies version consistency
- Builds the package
- Validates with twine
- Publishes to TestPyPI or PyPI
- Uploads build artifacts

## Setup Required

### GitHub Secrets

Add these secrets to the repository:

1. **PYPI_API_TOKEN**
   - Get from: https://pypi.org/manage/account/token/
   - Add at: Repository Settings → Secrets → Actions

2. **TEST_PYPI_API_TOKEN**
   - Get from: https://test.pypi.org/manage/account/token/
   - Add at: Repository Settings → Secrets → Actions

## Usage

### Version Bumping & Release (Recommended)

**Option 1: Manual via GitHub Actions**
1. Go to Actions tab
2. Select "Manual Version Bump"
3. Click "Run workflow"
4. Choose bump type (patch/minor/major)
5. Workflow automatically:
   - Bumps version
   - Creates tag
   - Creates release
   - Triggers PyPI deployment

**Option 2: Local Script**
```bash
# Bump version locally
python .github/bump_version.py patch
git push origin main --tags
```

**Option 3: Automatic via Commit Messages**
```bash
# Commit with conventional format
git commit -m "feat: new feature"     # → minor bump
git commit -m "fix: bug fix"          # → patch bump
git commit -m "feat!: breaking change" # → major bump
git push origin main
```

### Manual PyPI Deployment

1. Go to Actions tab
2. Select "Publish to PyPI"
3. Click "Run workflow"
4. Choose environment (testpypi or pypi)
5. Click "Run workflow"

## Monitoring

View workflow status:
- Actions tab: https://github.com/Pymmdrza/spyhunt/actions
- Email notifications on failures
- Download artifacts from workflow runs

## Documentation

See [GITHUB_ACTIONS_DEPLOYMENT.md](../GITHUB_ACTIONS_DEPLOYMENT.md) for complete guide.

