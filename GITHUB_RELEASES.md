# GitHub Releases Process

## Creating a GitHub Release

1. **Prepare the release**:
   - Update version numbers in all relevant files
   - Update CHANGELOG.md with changes for this release
   - Update RELEASE_NOTES.md with detailed release notes
   - Commit all changes with a clear commit message

2. **Tag the release**:
   ```bash
   # Create an annotated tag
   git tag -a v1.0.0 -m "Release version 1.0.0"
   
   # Push tags to remote
   git push origin v1.0.0
   ```

3. **Create GitHub release via web interface**:
   - Go to the repository on GitHub
   - Click on "Releases" in the right sidebar
   - Click on "Draft a new release"
   - Select the tag you just created (v1.0.0)
   - Fill in the release title (e.g., "Version 1.0.0")
   - Paste the release notes from RELEASE_NOTES.md
   - Attach any relevant binaries if needed
   - Check "This is a pre-release" if appropriate
   - Click "Publish release"

4. **Alternative: Using GitHub CLI**:
   ```bash
   # Install GitHub CLI if not already installed
   # Then create release
   gh release create v1.0.0 --title "Version 1.0.0" --notes-file RELEASE_NOTES.md
   ```

## Release Assets

For future releases that might include binaries:

```bash
# Build any binaries needed for the release
# Then attach them during release creation

# Example for future binary releases:
gh release upload v1.0.0 dist/jsi-scraper-binary --clobber
```

## Release Validation Checklist

Before creating a release, ensure:

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is complete
- [ ] Version numbers are consistent across files
- [ ] Docker image builds successfully
- [ ] API endpoints work as expected
- [ ] Breaking changes are documented
- [ ] Security considerations are addressed