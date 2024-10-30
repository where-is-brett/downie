# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in Downie, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. Send an email to [hello@brettyang.au](mailto:hello@brettyang.au)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Possible impact
   - Suggestions for fixing (if any)

### What to expect:
- Acknowledgment within 24 hours
- Regular updates on the progress
- Credit in the security advisory (if desired)

## Security Best Practices

When using Downie:

1. Keep the software updated to the latest version
2. Use secure output directories
3. Validate input URLs
4. Be cautious with custom scripts
5. Review configurations before use

## Security Features

Downie includes several security features:

- URL validation
- Path traversal prevention
- Safe file handling
- Configurable SSL verification
- Rate limiting support

## Development Security

For developers:

1. Never commit sensitive information
2. Use security linters
3. Run security checks
4. Follow secure coding practices
5. Keep dependencies updated

## Known Issues

See our [Security Advisories](https://github.com/where-is-brett/downie/security/advisories) page for current and past security issues.