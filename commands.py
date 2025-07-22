"""
Discord command handlers for the British Virgin Islands Bot
"""
import logging
from typing import Optional
import discord
from discord import app_commands
from config import settings
from utils import (
    ChannelManager, EmbedBuilder, PermissionManager, 
    DMManager, ApplicationManager, RobloxAPI
)
from models import CitizenshipApplication, ApplicationStatus

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Centralized command handlers for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_citizenship_application(self, interaction: discord.Interaction):
        """Handle citizenship application command"""
        # Check if user already has a pending application
        if interaction.user.id in self.bot.pending_applications:
            await interaction.response.send_message(
                settings.messages.application_exists,
                ephemeral=True
            )
            return

        # Import CitizenshipModal dynamically to avoid circular imports
        from forms import CitizenshipModal
        
        # Send the modal
        modal = CitizenshipModal()
        await interaction.response.send_modal(modal)
    
    async def handle_citizenship_accept(self, interaction: discord.Interaction, user: discord.Member):
        """Handle citizenship acceptance command"""
        # Check citizenship management permissions (admin OR citizenship manager)
        user_role_ids = [role.id for role in interaction.user.roles]
        if not settings.has_citizenship_permission(user_role_ids):
            await interaction.response.send_message(
                settings.messages.no_citizenship_permission,
                ephemeral=True
            )
            return

        # Check if application exists
        application = ApplicationManager.find_application_by_user_id(
            self.bot.pending_applications, user.id
        )
        
        if not application:
            await interaction.response.send_message(
                settings.messages.no_application_found.format(user=user.mention),
                ephemeral=True
            )
            return

        # Update application status
        application.status = ApplicationStatus.APPROVED
        application.reviewed_by = str(interaction.user)

        # Remove from pending
        ApplicationManager.remove_application(self.bot.pending_applications, user.id)

        # Post to citizenship-status channel
        status_channel = ChannelManager.get_citizenship_status_channel(interaction.guild)
        if status_channel:
            embed = EmbedBuilder.create_approval_embed(user, interaction.user, application)
            await status_channel.send(embed=embed)

        # Send DM to applicant
        dm_embed = EmbedBuilder.create_dm_approval_embed()
        await DMManager.send_dm_safe(user, dm_embed)

        await interaction.response.send_message(
            settings.messages.approval_success.format(user=user.mention),
            ephemeral=True
        )
    
    async def handle_citizenship_decline(self, interaction: discord.Interaction, 
                                       user: discord.Member, reason: str = "No reason provided"):
        """Handle citizenship decline command"""
        # Check citizenship management permissions (admin OR citizenship manager)
        user_role_ids = [role.id for role in interaction.user.roles]
        if not settings.has_citizenship_permission(user_role_ids):
            await interaction.response.send_message(
                settings.messages.no_citizenship_permission,
                ephemeral=True
            )
            return

        # Check if application exists
        application = ApplicationManager.find_application_by_user_id(
            self.bot.pending_applications, user.id
        )
        
        if not application:
            await interaction.response.send_message(
                settings.messages.no_application_found.format(user=user.mention),
                ephemeral=True
            )
            return

        # Update application status
        application.status = ApplicationStatus.REJECTED
        application.reviewed_by = str(interaction.user)
        application.rejection_reason = reason

        # Remove from pending
        ApplicationManager.remove_application(self.bot.pending_applications, user.id)

        # Post to citizenship-status channel
        status_channel = ChannelManager.get_citizenship_status_channel(interaction.guild)
        if status_channel:
            embed = EmbedBuilder.create_decline_embed(user, interaction.user, reason)
            await status_channel.send(embed=embed)

        # Send DM to applicant
        dm_embed = EmbedBuilder.create_dm_decline_embed(reason)
        await DMManager.send_dm_safe(user, dm_embed)

        await interaction.response.send_message(
            settings.messages.decline_success.format(user=user.mention),
            ephemeral=True
        )
    
    async def handle_ban_command(self, interaction: discord.Interaction, user: discord.Member, 
                               place_id: str, reason: str = "No reason provided"):
        """Handle Roblox ban command"""
        # Check admin permissions (only admins can ban, not citizenship managers)
        user_role_ids = [role.id for role in interaction.user.roles]
        if not settings.has_admin_permission(user_role_ids):
            await interaction.response.send_message(
                settings.messages.no_ban_permission,
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Get user's Roblox username from their application
            roblox_username = ApplicationManager.get_roblox_username_from_applications(
                self.bot.pending_applications, user.id
            )

            if not roblox_username:
                await interaction.followup.send(
                    settings.messages.roblox_username_not_found.format(user=user.mention),
                    ephemeral=True
                )
                return

            # Execute ban through Roblox API
            success = await RobloxAPI.ban_user_from_place(
                roblox_username, place_id, reason, settings.get_roblox_api_key()
            )

            if success:
                # Create success embed
                embed = EmbedBuilder.create_ban_embed(
                    user, roblox_username, place_id, reason, interaction.user
                )

                await interaction.followup.send(embed=embed, ephemeral=True)

                # Log to moderation channel
                mod_log_channel = ChannelManager.get_mod_log_channel(interaction.guild)
                if mod_log_channel:
                    await mod_log_channel.send(embed=embed)

            else:
                await interaction.followup.send(
                    settings.messages.ban_failed,
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await interaction.followup.send(
                settings.messages.ban_error,
                ephemeral=True
            )