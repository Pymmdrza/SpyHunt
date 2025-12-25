# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated CI/CD.

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

### 2. `publish-to-pypi.yml` - Automated Deployment

**Triggers:**
- Automatic: When a GitHub release is published
- Manual: Via Actions tab (select TestPyPI or PyPI)

**What it does:**
- Builds the package
- Verifies with twine
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

### Automatic Deployment (Recommended)

1. Update version in `setup.py`, `pyproject.toml`, `__init__.py`
2. Create git tag: `git tag -a v4.0.1 -m "Release 4.0.1"`
3. Push: `git push origin main --tags`
4. Create GitHub Release
5. Workflow automatically deploys to PyPI

### Manual Deployment

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

