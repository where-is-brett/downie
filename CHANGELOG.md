# Changelog

## [v0.2.1] (2024-01-30)
### 🔒 Security
- Updated Jinja2 dependency to >=3.1.3 to address CVE-2019-8341
- Implemented security policy file for automated vulnerability scanning

### 🛠 Infrastructure
- Enhanced CI/CD pipeline with modern security scanning
- Updated development dependencies

## [v0.2.0] (2024-10-29)
### ⚠️ Breaking Changes
#### CLI Command Structure Redesign
Old commands:
```bash
downie download [url]
subtitle-dl download [url]
```
New commands:
```bash
downie video download [url]
downie subtitle download [url]
```

### 🔄 Changes
- Applied code formatting standards using black and isort
- Improved CLI documentation and help messages
- Enhanced inline code documentation

### 🐛 Bug Fixes
- Fixed subtitle CLI implementation to properly handle the `--auto-generated` flag
```bash
# Now working correctly
downie subtitle download [url] --auto-generated
```

## [v0.1.0] (Initial Release)
- First public release