"""
Utility functions for the British Virgin Islands Discord Bot
"""
import asyncio
import logging
from typing import Optional, Union
import discord
from config import settings

logger = logging.getLogger(__name__)

class ChannelManager:
    """Manages Discord channel operations"""
    
    @staticmethod
    def get_channel_by_id_or_name(guild: discord.Guild, channel_id: Optional[int], channel_name: str) -> Optional[discord.TextChannel]:
        """Get a text channel by ID first, then by name as fallback"""
        # Try by ID first (more reliable)
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                return channel
        
        # Fallback to name search
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel and isinstance(channel, discord.TextChannel):
            return channel
        return None
    
    @staticmethod
    def get_channel_by_name(guild: discord.Guild, channel_name: str) -> Optional[discord.TextChannel]:
        """Get a text channel by name from a guild"""
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel and isinstance(channel, discord.TextChannel):
            return channel
        return None
    
    @staticmethod
    def get_citizenship_log_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the citizenship log channel"""
        return ChannelManager.get_channel_by_id_or_name(
            guild, 
            settings.channels.citizenship_log_id, 
            settings.channels.citizenship_log
        )
    
    @staticmethod
    def get_citizenship_status_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the citizenship status channel"""
        return ChannelManager.get_channel_by_id_or_name(
            guild, 
            settings.channels.citizenship_status_id, 
            settings.channels.citizenship_status
        )
    
    @staticmethod
    def get_mod_log_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the moderation log channel"""
        return ChannelManager.get_channel_by_id_or_name(
            guild, 
            settings.channels.mod_log_id, 
            settings.channels.mod_log
        )

class EmbedBuilder:
    """Builds Discord embeds with consistent styling"""
    
    @staticmethod
    def create_base_embed(title: str, color: int, description: str = None) -> discord.Embed:
        """Create a base embed with common settings"""
        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        if description:
            embed.description = description
        return embed
    
    @staticmethod
    def create_application_embed(application, user: discord.User) -> discord.Embed:
        """Create an embed for a new citizenship application"""
        embed = EmbedBuilder.create_base_embed(
            title="New Citizenship Application",
            color=settings.embeds.application_submitted
        )
        
        embed.add_field(
            name="Applicant", 
            value=f"{user.mention} ({user})", 
            inline=False
        )
        embed.add_field(
            name="Roblox Username", 
            value=application.roblox_username, 
            inline=True
        )
        embed.add_field(
            name="Discord Username", 
            value=application.discord_username, 
            inline=True
        )
        
        # Truncate long reason if needed
        reason = application.reason
        if len(reason) > 500:
            reason = reason[:500] + "..."
        embed.add_field(name="Reason", value=reason, inline=False)
        
        embed.add_field(
            name="Criminal Record", 
            value=application.criminal_record, 
            inline=False
        )
        
        if application.additional_info:
            additional_info = application.additional_info
            if len(additional_info) > 500:
                additional_info = additional_info[:500] + "..."
            embed.add_field(
                name="Additional Info", 
                value=additional_info, 
                inline=False
            )
        
        embed.set_footer(text=f"Application ID: {application.user_id}")
        return embed
    
    @staticmethod
    def create_approval_embed(user: discord.Member, reviewer: discord.User, application) -> discord.Embed:
        """Create an embed for application approval"""
        embed = EmbedBuilder.create_base_embed(
            title="✅ Citizenship Application Approved",
            color=settings.embeds.application_approved
        )
        
        embed.add_field(name="Applicant", value=user.mention, inline=True)
        embed.add_field(name="Reviewed by", value=reviewer.mention, inline=True)
        embed.add_field(name="Roblox Username", value=application.roblox_username, inline=True)
        embed.set_footer(text="Welcome to the British Virgin Islands!")
        
        return embed
    
    @staticmethod
    def create_decline_embed(user: discord.Member, reviewer: discord.User, reason: str) -> discord.Embed:
        """Create an embed for application decline"""
        embed = EmbedBuilder.create_base_embed(
            title="❌ Citizenship Application Declined",
            color=settings.embeds.application_declined
        )
        
        embed.add_field(name="Applicant", value=user.mention, inline=True)
        embed.add_field(name="Reviewed by", value=reviewer.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        return embed
    
    @staticmethod
    def create_ban_embed(user: discord.Member, roblox_username: str, place_id: str, 
                        reason: str, banned_by: discord.User) -> discord.Embed:
        """Create an embed for Roblox ban execution"""
        embed = EmbedBuilder.create_base_embed(
            title="🔨 Roblox Ban Executed",
            color=settings.embeds.ban_executed
        )
        
        embed.add_field(name="Discord User", value=user.mention, inline=True)
        embed.add_field(name="Roblox Username", value=roblox_username, inline=True)
        embed.add_field(name="Place ID", value=place_id, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=banned_by.mention, inline=True)
        
        return embed
    
    @staticmethod
    def create_dm_approval_embed() -> discord.Embed:
        """Create DM embed for application approval"""
        embed = EmbedBuilder.create_base_embed(
            title=settings.messages.approval_dm_title,
            description=settings.messages.approval_dm_description,
            color=settings.embeds.application_approved
        )
        
        embed.add_field(
            name="What's Next?", 
            value=settings.messages.approval_dm_next_steps, 
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_dm_decline_embed(reason: str) -> discord.Embed:
        """Create DM embed for application decline"""
        embed = EmbedBuilder.create_base_embed(
            title=settings.messages.decline_dm_title,
            description=settings.messages.decline_dm_description,
            color=settings.embeds.application_declined
        )
        
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(
            name="Next Steps", 
            value=settings.messages.decline_dm_next_steps, 
            inline=False
        )
        
        return embed

class PermissionManager:
    """Manages user permissions"""
    
    @staticmethod
    def has_admin_role(member: discord.Member, admin_role_id: int) -> bool:
        """Check if member has the required admin role"""
        if admin_role_id == 0:
            logger.warning("Admin role ID not configured")
            return False
        
        return any(role.id == admin_role_id for role in member.roles)
    
    @staticmethod
    def has_citizenship_manager_role(member: discord.Member, citizenship_manager_role_id: int) -> bool:
        """Check if member has the required citizenship manager role"""
        if citizenship_manager_role_id == 0:
            logger.warning("Citizenship manager role ID not configured")
            return False
        
        return any(role.id == citizenship_manager_role_id for role in member.roles)
    
    @staticmethod
    def can_manage_citizenship(member: discord.Member, admin_role_id: int, citizenship_manager_role_id: int) -> bool:
        """Check if member can manage citizenship applications (admin OR citizenship manager)"""
        return (PermissionManager.has_admin_role(member, admin_role_id) or 
                PermissionManager.has_citizenship_manager_role(member, citizenship_manager_role_id))
    
    @staticmethod
    def can_ban_users(member: discord.Member, admin_role_id: int) -> bool:
        """Check if member can ban users (only admins can ban)"""
        return PermissionManager.has_admin_role(member, admin_role_id)

class DMManager:
    """Manages direct message operations"""
    
    @staticmethod
    async def send_dm_safe(user: Union[discord.User, discord.Member], embed: discord.Embed) -> bool:
        """Safely send a DM to a user, handling Forbidden errors"""
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user}")
            return False
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")
            return False

class ValidationHelper:
    """Helper functions for data validation"""
    
    @staticmethod
    def is_valid_place_id(place_id: str) -> bool:
        """Validate Roblox place ID format"""
        try:
            int(place_id)
            return len(place_id) > 0
        except ValueError:
            return False
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to max length with suffix"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

class ApplicationManager:
    """Manages citizenship application operations"""
    
    @staticmethod
    def find_application_by_user_id(applications: dict, user_id: int):
        """Find application by user ID"""
        return applications.get(user_id)
    
    @staticmethod
    def get_roblox_username_from_applications(applications: dict, user_id: int) -> Optional[str]:
        """Get Roblox username from user's application"""
        for app in applications.values():
            if app.user_id == user_id:
                return app.roblox_username
        return None
    
    @staticmethod
    def remove_application(applications: dict, user_id: int) -> bool:
        """Remove application from pending list"""
        if user_id in applications:
            del applications[user_id]
            return True
        return False

class RobloxAPI:
    """Placeholder class for Roblox API integration"""
    
    @staticmethod
    async def ban_user_from_place(username: str, place_id: str, reason: str, api_key: str) -> bool:
        """
        Placeholder function for Roblox API integration
        In a real implementation, this would make API calls to Roblox
        """
        try:
            logger.info(f"Attempting to ban {username} from place {place_id} for: {reason}")
            
            # Example of what a real implementation might look like:
            # headers = {'Authorization': f'Bearer {api_key}'}
            # data = {
            #     'username': username,
            #     'place_id': place_id,
            #     'reason': reason
            # }
            # async with aiohttp.ClientSession() as session:
            #     async with session.post('https://api.roblox.com/v1/bans', 
            #                           headers=headers, json=data) as response:
            #         return response.status == 200
            
            # For now, simulate success with delay
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error banning from Roblox: {e}")
            return False