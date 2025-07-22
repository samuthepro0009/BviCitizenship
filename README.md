# British Virgin Islands Discord Bot

A comprehensive, modular Discord bot for managing BVI citizenship applications with interactive forms, admin approval workflows, and Roblox integration.

## 🏗️ Architecture Overview

The bot follows a clean, modular architecture with complete separation of concerns:

```
├── config.py         # Centralized configuration system
├── bot.py            # Main bot implementation  
├── commands.py       # Command handlers
├── forms.py          # Discord UI forms/modals
├── utils.py          # Utility classes and helpers
├── models.py         # Data models and enums
├── keep_alive.py     # Health monitoring service
└── main.py           # Application entry point
```

## ⚙️ Configuration System

### Flexible Settings (`config.py`)

All bot behavior is controlled through a comprehensive settings system:

- **Channel Configuration**: Customize channel names for logs and status updates
- **Message Templates**: Modify all user-facing messages and responses  
- **Embed Styling**: Configure colors and appearance of Discord embeds
- **Form Fields**: Adjust form labels, placeholders, and length limits
- **Command Settings**: Customize command names and descriptions
- **Bot Behavior**: Control timing, logging, and API settings

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DISCORD_BOT_TOKEN` | Bot authentication | Required |
| `ADMIN_ROLE_ID` | Role ID for full admin permissions | `0` (disabled) |
| `CITIZENSHIP_MANAGER_ROLE_ID` | Role ID for citizenship management only | `0` (disabled) |
| `ROBLOX_API_KEY` | Roblox API integration | `placeholder_key` |
| `PORT` | Flask server port | `5000` |
| `RENDER_EXTERNAL_URL` | External URL for health checks | `http://localhost:5000` |

## 🎯 Features

### Citizenship Application System
- **Interactive Forms**: Modern Discord modals with validation
- **Application Tracking**: In-memory storage with status management
- **Channel Logging**: Automatic posting to designated channels
- **DM Notifications**: Private messages to applicants with results

### Admin Management
- **Dual-Tier Permissions**: Separate Admin and Citizenship Manager roles
- **Granular Access Control**: Citizenship Managers can approve/decline but not ban users
- **Review Commands**: Accept/decline applications with reasons
- **Audit Trail**: All actions logged with timestamps and reviewers

### Roblox Integration
- **Ban System**: Placeholder API integration for place-based bans
- **Username Linking**: Applications linked to Roblox usernames
- **Extensible Design**: Easy to implement real Roblox API calls

### Infrastructure
- **Keep-Alive Service**: Prevents bot sleeping on hosting platforms
- **Health Monitoring**: Multiple endpoints for status checking
- **Error Handling**: Comprehensive error catching and logging
- **Modular Design**: Easy to extend and maintain

## 🚀 Quick Setup

### 1. Discord Bot Setup
```bash
# Create bot at https://discord.com/developers/applications
# Enable these permissions:
# - applications.commands (slash commands)
# - Send Messages, Embed Links, Use Slash Commands
```

### 2. Environment Configuration
Add to Replit Secrets:
```
DISCORD_BOT_TOKEN=your_bot_token_here
ADMIN_ROLE_ID=123456789012345678  # Optional: Role ID for full admins
CITIZENSHIP_MANAGER_ROLE_ID=987654321098765432  # Optional: Role ID for citizenship managers
```

#### Permission System Setup
- **Admin Role**: Can approve/decline applications AND ban users from Roblox
- **Citizenship Manager Role**: Can approve/decline applications but CANNOT ban users
- **No Roles**: If both role IDs are 0, anyone can use commands (not recommended)

To get role IDs:
1. Enable Developer Mode in Discord (Settings > Appearance > Developer Mode)
2. Right-click on the role in Server Settings > Roles
3. Click "Copy Role ID"

### 3. Discord Server Setup
Create these channels in your server:
- `#citizenship-log` - Application submissions
- `#citizenship-status` - Approval/rejection announcements  
- `#mod-log` - Ban and moderation actions

### 4. Bot Invitation
Invite bot with scopes: `applications.commands` and `bot`

## 📋 Available Commands

### User Commands
- `/citizenship` - Submit citizenship application form

### Admin Commands 

#### Citizenship Management (Admin or Citizenship Manager role)
- `/citizenship_accept <user>` - Approve pending application
- `/citizenship_decline <user> [reason]` - Reject application with reason

#### Full Admin Commands (Admin role only)
- `/ban <user> <place_id> [reason]` - Ban user from Roblox place

## 🛠️ Customization Guide

### Modifying Messages
Edit `config.py` → `MessageConfig` class:
```python
@dataclass
class MessageConfig:
    application_success: str = "Your custom success message"
    no_permission: str = "Custom permission denied message"
    # ... etc
```

### Changing Channel Names
Edit `config.py` → `ChannelConfig` class:
```python
@dataclass  
class ChannelConfig:
    citizenship_log: str = "your-custom-log-channel"
    citizenship_status: str = "your-custom-status-channel"
    mod_log: str = "your-custom-mod-channel"
```

### Form Customization
Edit `config.py` → `FormConfig` class:
```python
@dataclass
class FormConfig:
    reason_label: str = "Why do you want citizenship?"
    reason_max_length: int = 2000  # Increase limit
    # ... etc
```

### Adding New Commands
1. Add handler to `commands.py` → `CommandHandlers` class
2. Register command in `bot.py` → `_setup_commands()` method
3. Update command configuration in `config.py`

## 🔧 Advanced Features

### Health Monitoring Endpoints
- `GET /` - Basic health check
- `GET /health` - JSON health status
- `GET /status` - Extended configuration info

### Logging System
Comprehensive logging with configurable levels:
```python
# In config.py
log_level: int = logging.INFO
log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Error Handling
- Graceful command error handling
- DM failure protection  
- Channel not found warnings
- API timeout handling

## 🔌 Roblox API Integration

The bot includes a placeholder Roblox API system ready for implementation:

```python
# In utils.py → RobloxAPI class
async def ban_user_from_place(username: str, place_id: str, reason: str, api_key: str) -> bool:
    # Replace placeholder with actual Roblox API calls
    # Example implementation provided in comments
    pass
```

## 🚀 Deployment

The bot includes a robust keep-alive system for deployment on platforms like Render, Railway, or Heroku:

1. **Flask Health Server**: Runs on configurable port
2. **Self-Ping System**: Prevents service hibernation  
3. **Multiple Health Endpoints**: For external monitoring
4. **Graceful Error Handling**: Service continues despite individual failures

## 📈 Monitoring & Logs

View real-time logs to monitor:
- Application submissions and reviews
- Command usage and errors
- Keep-alive ping status
- Configuration warnings

The bot provides detailed logging for all operations while maintaining user privacy.

## 🤝 Contributing

The modular architecture makes it easy to extend:

1. **Add New Models**: Extend `models.py`
2. **Create New Utilities**: Add to `utils.py`  
3. **Implement New Commands**: Follow patterns in `commands.py`
4. **Update Configuration**: Add new settings to `config.py`

All changes automatically benefit from the existing error handling, logging, and configuration systems.