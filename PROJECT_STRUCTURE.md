# Project Structure

Complete overview of the Vinted Price Tracker Bot project files and their purposes.

## Directory Tree

```
Vinted_price_tracker/
│
├── .github/
│   └── workflows/
│       └── vinted_price_update.yml    # GitHub Actions workflow
│
├── vinted_price_bot.py                # Main bot script
├── test_connection.py                 # Connection testing utility
├── setup.py                           # Interactive setup wizard
│
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
├── .env.example                      # Environment variable template
│
├── Dockerfile                        # Docker container definition
├── docker-compose.yml                # Docker Compose configuration
│
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick start guide
├── GITHUB_SECRETS_SETUP.md          # GitHub Actions setup guide
├── GOOGLE_SHEETS_TEMPLATE.md        # Google Sheets usage guide
├── PROJECT_STRUCTURE.md             # This file
├── CHANGELOG.md                      # Version history
├── LICENSE                           # MIT License
│
└── (user creates these):
    ├── .env                          # Your environment variables
    └── service_account.json          # Google service account key
```

## File Descriptions

### Core Application Files

#### `vinted_price_bot.py`
**Purpose:** Main bot application  
**Features:**
- Vinted login automation
- Item scraping from profile
- Google Sheets synchronization
- Price calculation and updates
- Logging and error handling

**Key Classes:**
- `VintedPriceBot`: Main bot controller

**Key Methods:**
- `setup_driver()`: Initialize Selenium WebDriver
- `setup_google_sheets()`: Connect to Google Sheets
- `login_to_vinted()`: Authenticate with Vinted
- `get_listed_items()`: Scrape user's items
- `sync_with_google_sheets()`: Sync data with sheets
- `update_item_price()`: Update individual item price
- `run()`: Main execution flow

### Utility Scripts

#### `test_connection.py`
**Purpose:** Test all connections before deployment  
**Tests:**
- Environment variables validation
- Selenium WebDriver setup
- Google Sheets API connection
- Vinted website accessibility

**Usage:**
```bash
python test_connection.py
```

#### `setup.py`
**Purpose:** Interactive setup wizard  
**Features:**
- Create .env file with prompts
- Check for service_account.json
- Install dependencies
- Guide user through setup

**Usage:**
```bash
python setup.py
```

### Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies  
**Packages:**
- `selenium` - Web automation
- `webdriver-manager` - ChromeDriver management
- `gspread` - Google Sheets API
- `google-auth` - Google authentication
- `python-dotenv` - Environment variables
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing

#### `.env.example`
**Purpose:** Template for environment variables  
**Variables:**
- `VINTED_EMAIL` - Vinted login email
- `VINTED_PASSWORD` - Vinted login password
- `VINTED_PROFILE_URL` - Your profile URL
- `GOOGLE_SHEET_ID` - Google Sheet identifier
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Path to credentials
- `DEFAULT_PRICE_CHANGE_PERCENT` - Default percentage

#### `.gitignore`
**Purpose:** Prevent sensitive files from Git tracking  
**Ignores:**
- `.env` - Environment variables
- `service_account.json` - Google credentials
- `__pycache__/` - Python cache
- `*.log` - Log files
- Virtual environments

### Docker Files

#### `Dockerfile`
**Purpose:** Container image definition  
**Features:**
- Python 3.11 base image
- Chrome browser installation
- Dependency installation
- Application setup

**Usage:**
```bash
docker build -t vinted-bot .
docker run --env-file .env vinted-bot
```

#### `docker-compose.yml`
**Purpose:** Docker Compose orchestration  
**Features:**
- Service definition
- Volume mounts for logs
- Environment variable injection

**Usage:**
```bash
docker-compose up
```

### GitHub Actions

#### `.github/workflows/vinted_price_update.yml`
**Purpose:** Automated weekly execution  
**Triggers:**
- Cron schedule: Every Sunday 10 AM UTC
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Install Chrome
5. Create .env from secrets
6. Create service account JSON
7. Run bot
8. Upload logs as artifacts

**Configuration:**
- Runs on Ubuntu latest
- 30-day log retention
- Uses GitHub Secrets

### Documentation Files

#### `README.md`
**Purpose:** Main project documentation  
**Sections:**
- Features overview
- How it works
- Complete setup instructions
- Google Sheets guide
- GitHub Actions setup
- Local testing
- Troubleshooting
- Security notes
- Legal disclaimer

#### `QUICKSTART.md`
**Purpose:** Fast setup guide (5 minutes)  
**Sections:**
- Quick installation steps
- Minimal configuration
- Rapid deployment
- Basic usage

#### `GITHUB_SECRETS_SETUP.md`
**Purpose:** Detailed GitHub Secrets guide  
**Sections:**
- Step-by-step secret creation
- Each secret with examples
- Security best practices
- Workflow testing
- Troubleshooting

#### `GOOGLE_SHEETS_TEMPLATE.md`
**Purpose:** Google Sheets usage guide  
**Sections:**
- Sheet structure explanation
- Column descriptions
- Price calculation examples
- Pricing strategies
- Advanced formulas
- Tips and best practices

#### `PROJECT_STRUCTURE.md`
**Purpose:** This file - complete project overview  

#### `CHANGELOG.md`
**Purpose:** Version history and changes  
**Sections:**
- Version releases
- Features added
- Known issues
- Planned features

#### `LICENSE`
**Purpose:** MIT License terms  

### User-Created Files (Not in Repo)

#### `.env`
**Purpose:** Your environment variables  
**Created by:** `setup.py` or manually  
**Security:** ⚠️ Never commit to Git!

#### `service_account.json`
**Purpose:** Google Cloud service account credentials  
**Created by:** Google Cloud Console  
**Security:** ⚠️ Never commit to Git!

#### `vinted_bot.log`
**Purpose:** Application log file  
**Created by:** Bot during execution  
**Contains:** Timestamps, actions, errors, results

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│                   (Weekly Trigger)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              vinted_price_bot.py                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Setup Selenium + Login to Vinted             │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. Scrape Listed Items from Profile             │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. Connect to Google Sheets                     │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. Sync Data (Read Custom Percentages)         │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  5. Calculate New Prices                         │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  6. Update Prices on Vinted                      │  │
│  └─────────────┬────────────────────────────────────┘  │
│                ▼                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  7. Update Google Sheets with Results           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Languages
- **Python 3.11** - Main application language
- **YAML** - GitHub Actions workflow
- **Markdown** - Documentation

### Libraries
- **Selenium** - Web browser automation
- **gspread** - Google Sheets API wrapper
- **google-auth** - Google authentication
- **python-dotenv** - Environment management
- **beautifulsoup4** - HTML parsing

### Services
- **Google Sheets API** - Data storage
- **Google Drive API** - Sheet access
- **GitHub Actions** - Automation/scheduling
- **Chrome/Chromium** - Headless browser

### Infrastructure
- **Docker** - Optional containerization
- **Ubuntu** - GitHub Actions runner
- **Git** - Version control

## Security Model

```
┌─────────────────────────────────────────────────────────┐
│                 Sensitive Data                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Local Development:                                      │
│  ├── .env (gitignored)                                  │
│  └── service_account.json (gitignored)                  │
│                                                          │
│  GitHub Actions:                                         │
│  ├── GitHub Secrets (encrypted)                         │
│  └── Runtime only (not persisted)                       │
│                                                          │
│  Never Committed:                                        │
│  ├── Passwords                                          │
│  ├── API keys                                           │
│  └── Service account credentials                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Maintenance

### Regular Tasks
- ✅ Review logs weekly
- ✅ Update dependencies monthly
- ✅ Verify bot runs successfully
- ✅ Monitor for Vinted structure changes

### When Vinted Updates
- Check if selectors still work
- Update CSS selectors in code
- Test login flow
- Verify item scraping

### Updates
- Pull latest code
- Update dependencies: `pip install -U -r requirements.txt`
- Test locally before deploying
- Review CHANGELOG.md

## Support & Contributing

### Getting Help
1. Check documentation files
2. Review logs for errors
3. Run `test_connection.py`
4. Check GitHub Issues

### Contributing
1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Reporting Issues
Include:
- Error message (sanitized)
- Steps to reproduce
- Python version
- OS information
- Logs (remove sensitive data)

---

**Project Version:** 1.0.0  
**Last Updated:** 2026-01-18  
**License:** MIT

