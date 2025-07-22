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
        """Handle citizenship application command - show interactive dashboard"""
        try:
            # Import dashboard dynamically to avoid circular imports
            from forms import CitizenshipDashboard
            
            # Create the main dashboard embed with BVI banner
            embed = discord.Embed(
                title="🏴󠁧󠁢󠁥󠁮󠁧󠁿 British Virgin Islands Citizenship Services",
                color=settings.embeds.application_submitted,
                description="**Welcome to the British Virgin Islands Citizenship Portal**\n\n"
                           "Use the buttons below to:\n"
                           "• Apply for BVI citizenship\n"
                           "• Check your application status\n"
                           "• Learn about citizenship benefits\n"
                           "• Contact our support team\n\n"
                           "*Applications are reviewed by our citizenship management team*"
            )
            
            # Set the BVI banner image
            embed.set_image(url="https://i.imgur.com/G1wrrwI.png")
            embed.set_footer(text="British Virgin Islands • Citizenship Portal", icon_url="https://i.imgur.com/G1wrrwI.png")
            
            # Create the interactive dashboard
            dashboard = CitizenshipDashboard()
            
            # Send the embed with the interactive buttons
            await interaction.response.send_message(
                embed=embed, 
                view=dashboard, 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in citizenship application command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred. Please try again.",
                    ephemeral=True
                )
    
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
        try:
            dm_embed = discord.Embed(
                title="🎉 Citizenship Application Approved!",
                color=settings.embeds.application_approved,
                description="Congratulations! Your application for British Virgin Islands citizenship has been **approved**.\n\n"
                           "You are now officially a citizen of the British Virgin Islands! 🏴󠁧󠁢󠁥󠁮󠁧󠁿"
            )
            dm_embed.set_footer(text="British Virgin Islands • Citizenship Services")
            
            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent approval DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

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
        try:
            dm_embed = discord.Embed(
                title="❌ Citizenship Application Declined",
                color=settings.embeds.application_declined,
                description=f"Unfortunately, your application for British Virgin Islands citizenship has been **declined**.\n\n"
                           f"**Reason:** {reason}\n\n"
                           f"You may reapply in the future if circumstances change."
            )
            dm_embed.set_footer(text="British Virgin Islands • Citizenship Services")
            
            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent decline DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

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