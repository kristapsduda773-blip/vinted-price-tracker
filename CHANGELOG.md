# Changelog

All notable changes to the Vinted Price Tracker Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-18

### Added
- Initial release of Vinted Price Tracker Bot
- Automated price scraping from Vinted profiles
- Google Sheets integration for price management
- Customizable price change percentages per item
- Default 10% price change option
- Weekly automated runs via GitHub Actions
- Selenium-based web automation for Vinted interaction
- Headless Chrome browser support
- Comprehensive logging system
- Connection testing script (`test_connection.py`)
- Interactive setup wizard (`setup.py`)
- Docker support for containerized deployment
- GitHub Actions workflow with manual trigger option
- Detailed documentation:
  - Main README.md with full setup instructions
  - QUICKSTART.md for rapid deployment
  - GITHUB_SECRETS_SETUP.md for Actions configuration
  - GOOGLE_SHEETS_TEMPLATE.md for sheet usage guide
- Security features:
  - Environment variable management
  - .gitignore for sensitive files
  - GitHub Secrets integration
- Error handling and recovery mechanisms
- Support for positive and negative price changes
- Automatic Google Sheets structure creation
- Timestamp tracking for updates
- Log artifact retention in GitHub Actions

### Security
- Credentials stored securely in environment variables
- Service account JSON excluded from version control
- GitHub Secrets for CI/CD credentials
- No hardcoded sensitive information

### Documentation
- Comprehensive README with troubleshooting
- Quick start guide for fast setup
- Google Sheets usage examples
- GitHub Secrets setup walkthrough
- Docker deployment instructions
- MIT License

## [Unreleased]

### Planned Features
- Email notifications for price updates
- Support for multiple Vinted profiles
- Price history tracking
- Analytics dashboard
- Configurable retry logic
- Support for other Vinted country domains
- Multi-language support
- Scheduled price changes (future dates)
- Integration with Vinted message system
- Mobile app notifications
- Price optimization suggestions based on market data

### Known Issues
- Vinted may update their website structure, breaking selectors
- Login may fail with 2FA enabled (use app password)
- Rate limiting possible with frequent updates
- GitHub Actions may have cold start delays

---

## Version History

- **1.0.0** (2026-01-18) - Initial Release

