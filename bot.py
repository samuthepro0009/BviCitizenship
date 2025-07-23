"""
Main bot implementation for the British Virgin Islands Discord Bot
"""
import logging
from typing import Dict
import discord
from discord.ext import commands
from discord import app_commands
from config import settings
from commands import CommandHandlers
from advanced_features import EnhancedCitizenshipDashboard, application_tracker, AdminManagementCommands
from notification_system import notification_manager, NotificationType
from enhanced_admin_commands import setup_enhanced_admin_commands
from models import CitizenshipApplication
from comprehensive_logging import initialize_logger

# Set up logging
logger = settings.setup_logging()

class BVIBot(commands.Bot):
    """Main bot class for the British Virgin Islands Discord Bot"""
    
    def __init__(self):
        # Configure intents - only use default to avoid privileged intent errors
        intents = discord.Intents.default()
        
        super().__init__(
            command_prefix=settings.bot.command_prefix,
            intents=intents,
            help_command=None
        )
        
        # Initialize bot state
        self.pending_applications: Dict[int, CitizenshipApplication] = {}
        self.admin_role_id = settings.get_admin_role_id()
        self.citizenship_manager_role_id = settings.get_citizenship_manager_role_id()
        self.roblox_api_key = settings.get_roblox_api_key()
        
        # Initialize command handler
        self.command_handler = CommandHandlers(self)
        
        # Initialize comprehensive logger
        self.comprehensive_logger = None
        
        # Set up slash commands
        self._setup_commands()

    def _setup_commands(self):
        """Set up all slash commands"""
        
        @self.tree.command(
            name=settings.commands.citizenship_name, 
            description=settings.commands.citizenship_description
        )
        async def citizenship_command(interaction: discord.Interaction):
            await self.command_handler.handle_citizenship_application(interaction)

        @self.tree.command(
            name=settings.commands.accept_name, 
            description=settings.commands.accept_description
        )
        @app_commands.describe(user=settings.commands.accept_user_param)
        async def citizenship_accept_command(interaction: discord.Interaction, user: discord.Member):
            await self.command_handler.handle_citizenship_accept(interaction, user)

        @self.tree.command(
            name=settings.commands.decline_name, 
            description=settings.commands.decline_description
        )
        @app_commands.describe(
            user=settings.commands.decline_user_param,
            reason=settings.commands.decline_reason_param
        )
        async def citizenship_decline_command(
            interaction: discord.Interaction, 
            user: discord.Member, 
            reason: str = "No reason provided"
        ):
            await self.command_handler.handle_citizenship_decline(interaction, user, reason)

        @self.tree.command(
            name=settings.commands.ban_name, 
            description=settings.commands.ban_description
        )
        @app_commands.describe(
            user=settings.commands.ban_user_param,
            place_id=settings.commands.ban_place_id_param,
            reason=settings.commands.ban_reason_param
        )
        async def ban_command(
            interaction: discord.Interaction, 
            user: discord.Member, 
            place_id: str, 
            reason: str = "No reason provided"
        ):
            await self.command_handler.handle_ban_command(interaction, user, place_id, reason)

    async def on_ready(self):
        """Called when the bot is ready"""
        print(f"🤖 {self.user} connected to Discord")
        
        # Initialize comprehensive logger
        self.comprehensive_logger = initialize_logger(self)
        print("📋 Comprehensive logging system initialized")
        
        # Clear any existing applications to fix submitted_at errors
        self.pending_applications.clear()
        print("🧹 Cleared existing applications to prevent errors")
        
        try:
            synced = await self.tree.sync()
            print(f"⚡ Synced {len(synced)} slash commands")
            
            # Show configuration summary
            admin_roles = settings.get_admin_roles()
            citizenship_roles = settings.get_citizenship_manager_roles()
            print(f"🔧 Admin roles configured: {len(admin_roles)} roles")
            print(f"🔧 Citizenship manager roles: {len(citizenship_roles)} roles")
            print(f"🚀 BVI Discord Bot ready for citizenship applications!")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")

    async def on_member_join(self, member: discord.Member):
        """Called when a member joins the server"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_member_join(member)
        
        # Send welcome message
        try:
            await notification_manager.send_welcome_message(member)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    async def on_member_remove(self, member: discord.Member):
        """Called when a member leaves the server"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_member_leave(member)

    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Called when a member is banned"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_member_ban(guild, user)

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Called when a member is unbanned"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_member_unban(guild, user)

    async def on_message_delete(self, message: discord.Message):
        """Called when a message is deleted"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_message_delete(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Called when a message is edited"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_message_edit(before, after)

    async def on_guild_role_create(self, role: discord.Role):
        """Called when a role is created"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_role_create(role)

    async def on_guild_role_delete(self, role: discord.Role):
        """Called when a role is deleted"""
        if self.comprehensive_logger:
            await self.comprehensive_logger.log_role_delete(role)

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        print(f"❌ Command error: {error}")

    async def on_application_command_error(self, interaction: discord.Interaction, error):
        """Handle application command errors"""
        print(f"❌ Slash command error: {error}")
        
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ An error occurred while processing your command. Please try again later.",
                ephemeral=True
            )

def create_bot() -> BVIBot:
    """Factory function to create and configure the bot"""
    return BVIBot()

def run_bot():
    """Run the bot with the Discord token"""
    token = settings.get_discord_token()
    if not token:
        logger.error(f"{settings.bot.discord_token_env} environment variable not set")
        return
    
    bot = create_bot()
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    run_bot()