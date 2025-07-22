"""
Configuration settings for the British Virgin Islands Discord Bot
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

# =========================================
# CHANNEL CONFIGURATION
# =========================================

# Channel IDs for bot operations (preferred method)
CHANNEL_IDS = {
    "citizenship_log": 1397315480540151901,      # Channel for logging application submissions
    "citizenship_status": 1397315480540151903,   # Channel for posting approval/decline updates  
    "mod_log": 1397315480540151900               # Channel for moderation actions (bans, etc.)
}

# Channel names for bot operations (fallback method)
CHANNEL_NAMES = {
    "citizenship_log": "citizenship-log",      
    "citizenship_status": "citizenship-status", 
    "mod_log": "mod-log"                       
}

@dataclass
class ChannelConfig:
    """Configuration for Discord channels"""
    # Channel IDs (preferred - more reliable than names)
    citizenship_log_id: Optional[int] = CHANNEL_IDS["citizenship_log"]
    citizenship_status_id: Optional[int] = CHANNEL_IDS["citizenship_status"]
    mod_log_id: Optional[int] = CHANNEL_IDS["mod_log"]
    
    # Channel names (fallback if IDs not provided)
    citizenship_log: str = CHANNEL_NAMES["citizenship_log"]
    citizenship_status: str = CHANNEL_NAMES["citizenship_status"]
    mod_log: str = CHANNEL_NAMES["mod_log"]

@dataclass
class EmbedConfig:
    """Configuration for Discord embed colors and styling"""
    application_submitted: int = 0x3498db  # Blue
    application_approved: int = 0x2ecc71   # Green
    application_declined: int = 0xe74c3c   # Red
    ban_executed: int = 0xf39c12           # Orange
    error_color: int = 0x95a5a6            # Gray

@dataclass
class MessageConfig:
    """Configuration for bot messages"""
    # Application messages
    application_success: str = "✅ Your citizenship application has been submitted successfully! You will receive a DM once your application has been reviewed."
    application_exists: str = "❌ You already have a pending citizenship application. Please wait for it to be processed."
    
    # Permission messages
    no_permission: str = "❌ You don't have permission to use this command."
    no_citizenship_permission: str = "❌ You need the Admin or Citizenship Manager role to use this command."
    no_ban_permission: str = "❌ You need the Admin role to ban users."
    no_application_found: str = "❌ No pending application found for {user}."
    
    # Success messages
    approval_success: str = "✅ Successfully approved citizenship application for {user}"
    decline_success: str = "✅ Successfully declined citizenship application for {user}"
    
    # Error messages
    roblox_username_not_found: str = "❌ Could not find Roblox username for {user}. Make sure they have submitted a citizenship application with their Roblox username."
    ban_failed: str = "❌ Failed to ban user from Roblox place. Please check the place ID and try again."
    ban_error: str = "❌ An error occurred while processing the ban command."
    
    # DM messages
    approval_dm_title: str = "🎉 Citizenship Application Approved!"
    approval_dm_description: str = "Congratulations! Your application for British Virgin Islands citizenship has been approved."
    approval_dm_next_steps: str = "You are now officially a citizen of the British Virgin Islands!"
    
    decline_dm_title: str = "❌ Citizenship Application Declined"
    decline_dm_description: str = "Unfortunately, your application for British Virgin Islands citizenship has been declined."
    decline_dm_next_steps: str = "You may reapply in the future if circumstances change."

@dataclass
class FormConfig:
    """Configuration for application form fields"""
    roblox_username_label: str = "What is your Roblox username?"
    roblox_username_placeholder: str = "Enter your Roblox username..."
    roblox_username_max_length: int = 50
    
    discord_username_label: str = "What is your Discord username?"
    discord_username_placeholder: str = "Enter your Discord username..."
    discord_username_max_length: int = 50
    
    reason_label: str = "Why do you want to become a BVI citizen?"
    reason_placeholder: str = "Please explain your motivation..."
    reason_max_length: int = 1000
    
    criminal_record_label: str = "Have you been convicted of any crimes?"
    criminal_record_placeholder: str = "Yes/No and details if applicable..."
    criminal_record_max_length: int = 500
    
    additional_info_label: str = "Any additional information?"
    additional_info_placeholder: str = "Optional additional information..."
    additional_info_max_length: int = 500

@dataclass
class CommandConfig:
    """Configuration for slash commands"""
    citizenship_name: str = "citizenship"
    citizenship_description: str = "Apply for British Virgin Islands citizenship"
    
    accept_name: str = "citizenship_accept"
    accept_description: str = "Accept a citizenship application"
    accept_user_param: str = "The user whose application to accept"
    
    decline_name: str = "citizenship_decline"
    decline_description: str = "Decline a citizenship application"
    decline_user_param: str = "The user whose application to decline"
    decline_reason_param: str = "Reason for declining the application"
    
    ban_name: str = "ban"
    ban_description: str = "Ban a user from a Roblox place"
    ban_user_param: str = "The Discord user to ban"
    ban_place_id_param: str = "The Roblox place ID to ban from"
    ban_reason_param: str = "Reason for the ban"

# =========================================  
# ROLE CONFIGURATION
# =========================================

# Admin roles (full permissions: ban users, manage citizenship)
ADMIN_ROLES = [
    # Add your admin role IDs here, one per line
    # Example:
    1397315477163868309,
    # 123123213,
]

# Citizenship manager roles (citizenship management only, cannot ban users)  
CITIZENSHIP_MANAGER_ROLES = [
    # Add your citizenship manager role IDs here, one per line
    # Example:
    1397315477163868309,
    # 8425523532,
]

@dataclass
class RoleConfig:
    """Configuration for Discord roles"""
    admin_roles: Optional[List[int]] = None
    citizenship_manager_roles: Optional[List[int]] = None
    
    def __post_init__(self):
        """Initialize role lists from global constants"""
        if self.admin_roles is None:
            self.admin_roles = ADMIN_ROLES.copy()
        if self.citizenship_manager_roles is None:
            self.citizenship_manager_roles = CITIZENSHIP_MANAGER_ROLES.copy()
    
    def is_admin(self, user_roles: List[int]) -> bool:
        """Check if user has admin permissions"""
        return any(role_id in self.admin_roles for role_id in user_roles)
    
    def is_citizenship_manager(self, user_roles: List[int]) -> bool:
        """Check if user has citizenship management permissions"""
        return any(role_id in self.citizenship_manager_roles for role_id in user_roles)
    
    def has_citizenship_permissions(self, user_roles: List[int]) -> bool:
        """Check if user has citizenship management permissions (admin OR citizenship manager)"""
        return self.is_admin(user_roles) or self.is_citizenship_manager(user_roles)

@dataclass
class BotConfig:
    """Main bot configuration"""
    # Discord settings
    bot_name: str = "British Virgin Islands"
    command_prefix: str = "!"
    
    # Environment variables (legacy support)
    discord_token_env: str = "DISCORD_BOT_TOKEN"
    admin_role_id_env: str = "ADMIN_ROLE_ID"
    citizenship_manager_role_id_env: str = "CITIZENSHIP_MANAGER_ROLE_ID"
    roblox_api_key_env: str = "ROBLOX_API_KEY"
    port_env: str = "PORT"
    render_url_env: str = "RENDER_EXTERNAL_URL"
    
    # Default values
    default_port: int = 5000
    default_admin_role_id: int = 0
    default_citizenship_manager_role_id: int = 0
    default_roblox_api_key: str = "placeholder_key"
    
    # Timing settings
    keep_alive_interval: int = 30  # seconds
    api_timeout: int = 10  # seconds
    
    # Logging
    log_level: int = logging.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class Settings:
    """Central settings manager"""
    
    def __init__(self):
        self.channels = ChannelConfig()
        self.embeds = EmbedConfig()
        self.messages = MessageConfig()
        self.forms = FormConfig()
        self.commands = CommandConfig()
        self.bot = BotConfig()
        self.roles = RoleConfig()
        
    def get_discord_token(self) -> Optional[str]:
        """Get Discord bot token from environment"""
        return os.getenv(self.bot.discord_token_env)
    
    def get_admin_role_id(self) -> int:
        """Get admin role ID from environment (legacy support)"""
        try:
            return int(os.getenv(self.bot.admin_role_id_env, str(self.bot.default_admin_role_id)))
        except (ValueError, TypeError):
            return self.bot.default_admin_role_id
    
    def get_citizenship_manager_role_id(self) -> int:
        """Get citizenship manager role ID from environment (legacy support)"""
        try:
            return int(os.getenv(self.bot.citizenship_manager_role_id_env, str(self.bot.default_citizenship_manager_role_id)))
        except (ValueError, TypeError):
            return self.bot.default_citizenship_manager_role_id
    
    def get_admin_roles(self) -> List[int]:
        """Get list of admin role IDs"""
        # Combine configured roles with legacy environment variable
        roles = self.roles.admin_roles.copy()
        legacy_role = self.get_admin_role_id()
        if legacy_role != 0 and legacy_role not in roles:
            roles.append(legacy_role)
        return roles
    
    def get_citizenship_manager_roles(self) -> List[int]:
        """Get list of citizenship manager role IDs"""
        # Combine configured roles with legacy environment variable
        roles = self.roles.citizenship_manager_roles.copy()
        legacy_role = self.get_citizenship_manager_role_id()
        if legacy_role != 0 and legacy_role not in roles:
            roles.append(legacy_role)
        return roles
    
    def has_admin_permission(self, user_roles: List[int]) -> bool:
        """Check if user has admin permissions"""
        admin_roles = self.get_admin_roles()
        return any(role_id in admin_roles for role_id in user_roles)
    
    def has_citizenship_permission(self, user_roles: List[int]) -> bool:
        """Check if user has citizenship management permissions"""
        admin_roles = self.get_admin_roles()
        citizenship_roles = self.get_citizenship_manager_roles()
        all_authorized_roles = admin_roles + citizenship_roles
        return any(role_id in all_authorized_roles for role_id in user_roles)
    
    def get_roblox_api_key(self) -> str:
        """Get Roblox API key from environment"""
        return os.getenv(self.bot.roblox_api_key_env, self.bot.default_roblox_api_key)
    
    def get_port(self) -> int:
        """Get port from environment"""
        try:
            return int(os.getenv(self.bot.port_env, str(self.bot.default_port)))
        except (ValueError, TypeError):
            return self.bot.default_port
    
    def get_render_url(self) -> str:
        """Get Render external URL from environment"""
        return os.getenv(self.bot.render_url_env, f"http://localhost:{self.get_port()}")
    
    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=self.bot.log_level,
            format=self.bot.log_format
        )
        return logging.getLogger(__name__)

# Global settings instance
settings = Settings()