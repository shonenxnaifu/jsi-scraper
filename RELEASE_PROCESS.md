# Release Process Documentation

This document outlines the complete release process for JSI Scraper.

## Pre-Release Checklist

Before starting a release, ensure:

- [ ] All feature work is completed and tested
- [ ] All automated tests pass
- [ ] Code has been reviewed and approved
- [ ] Dependencies are up-to-date and secure
- [ ] Documentation is updated
- [ ] Breaking changes are documented

## Release Steps

### 1. Prepare the Release

1. **Update version number**:
   - Update `app/__version__.py` with the new version
   - Update `VERSION` file in the root directory
   - Any other files that contain version information

2. **Update changelog**:
   - Modify `CHANGELOG.md` following Keep a Changelog format
   - Add new version section with changes
   - Update date of release

3. **Update release notes**:
   - Modify `RELEASE_NOTES.md` with detailed information for this release
   - Include new features, improvements, bug fixes, and breaking changes

4. **Test the application**:
   - Run all tests to ensure everything works
   - Test both local and Docker deployments
   - Verify API endpoints return expected data

### 2. Commit Release Changes

```bash
# Create a release commit
git add .
git commit -m "release: version X.Y.Z"
git push origin main
```

### 3. Create Git Tag

```bash
# Create and push annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```

### 4. Build and Test Docker Image

```bash
# Build Docker image with version tag
docker build -t jsi-scraper:vX.Y.Z .

# Test the Docker image
docker run -p 8000:8000 jsi-scraper:vX.Y.Z

# If testing passes, tag as latest
docker tag jsi-scraper:vX.Y.Z jsi-scraper:latest
```

### 5. Create GitHub Release

1. Go to GitHub repository releases page
2. Click "Draft a new release"
3. Select the tag just created
4. Fill in release title (e.g. "Version X.Y.Z")
5. Paste release notes content
6. Attach any necessary assets (if applicable)
7. Publish the release

### 6. Publish Docker Image

```bash
# Tag for your container registry
docker tag jsi-scraper:vX.Y.Z your-registry/jsi-scraper:vX.Y.Z

# Push to registry
docker push your-registry/jsi-scraper:vX.Y.Z

# Push latest tag
docker push your-registry/jsi-scraper:latest
```

## Post-Release Tasks

- [ ] Announce release internally/externally as appropriate
- [ ] Update any deployment configurations to use new version
- [ ] Monitor application after deployment for issues
- [ ] Close related issues and milestones in issue tracker

## Versioning Strategy

This project follows Semantic Versioning (SemVer):

- **MAJOR** version for incompatible API changes (X.0.0)
- **MINOR** version for backwards-compatible functionality (1.X.0) 
- **PATCH** version for backwards-compatible bug fixes (1.0.X)

## Automation Opportunities

For future enhancement, consider automating:

- Running tests before release
- Building and publishing Docker images
- Creating GitHub releases
- Publishing to package registries
- Notification to teams about releases

## Release Branch Strategy (Optional)

For more complex projects, consider using release branches:

```bash
# Create release branch
git checkout -b release/vX.Y.Z main

# After testing and fixes, merge back to main
git checkout main
git merge release/vX.Y.Z
git branch -d release/vX.Y.Z
```