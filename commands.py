"""
Discord command handlers for the British Virgin Islands Bot
"""
import logging
import os
from typing import Optional
import discord
from discord import app_commands
from config import settings
from utils import (
    ChannelManager, EmbedBuilder, PermissionManager, 
    DMManager, ApplicationManager
)
from models import CitizenshipApplication, ApplicationStatus
from image_config import get_image_url

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Centralized command handlers for the bot"""

    def __init__(self, bot):
        self.bot = bot

    async def handle_citizenship_application(self, interaction: discord.Interaction):
        """Handle citizenship application command - show interactive dashboard"""
        try:
            # Don't defer - respond immediately with the embed
            
            # Import enhanced dashboard dynamically to avoid circular imports
            from advanced_features import EnhancedCitizenshipDashboard, application_tracker

            # Create the main dashboard embed with professional styling
            embed = discord.Embed(
                title="British Virgin Islands Citizenship Services",
                color=0x1e3a8a,  # Professional navy blue
                description="**Welcome to the Official BVI Citizenship Portal**\n\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           "**Available Services:**\n"
                           "🗳️ Apply for BVI citizenship\n"
                           "📊 Check your application status\n"
                           "📋 Learn about citizenship benefits\n"
                           "🎧 Contact our support team\n\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           "*All applications are reviewed by our certified citizenship management team*"
            )

            # Use the uploaded BVI coat of arms images from imgur
            embed.set_image(url=get_image_url("banner"))

            # Set the footer with BVI coat of arms icon
            embed.set_footer(
                text="Government of the British Virgin Islands | Department of Immigration", 
                icon_url=get_image_url("footer_icon")
            )

            # Add thumbnail for additional branding
            embed.set_thumbnail(url=get_image_url("thumbnail"))

            # Create the enhanced interactive dashboard
            dashboard = EnhancedCitizenshipDashboard(application_tracker)

            # Send the embed with the interactive buttons using response
            await interaction.response.send_message(
                embed=embed, 
                view=dashboard, 
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Error in citizenship application command: {e}")
            # Don't try to respond on timeout errors to prevent double acknowledgment
            if "Unknown interaction" not in str(e):
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ An error occurred. Please try again.",
                            ephemeral=True
                        )
                    else:
                        await interaction.followup.send(
                            "❌ An error occurred. Please try again.",
                            ephemeral=True
                        )
                except Exception as follow_error:
                    print(f"❌ Failed to send error message: {follow_error}")

    async def handle_citizenship_accept(self, interaction: discord.Interaction, user: discord.Member):
        """Handle citizenship acceptance command"""
        # Check citizenship management permissions (admin OR citizenship manager)
        if hasattr(interaction.user, 'roles') and interaction.user.roles:
            user_role_ids = [role.id for role in interaction.user.roles]
            if not settings.has_citizenship_permission(user_role_ids):
                await interaction.response.send_message(
                    settings.messages.no_citizenship_permission,
                    ephemeral=True
                )
                return
        else:
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
        if interaction.guild:
            status_channel = ChannelManager.get_citizenship_status_channel(interaction.guild)
            if status_channel:
                embed = EmbedBuilder.create_approval_embed(user, interaction.user, application)
                await status_channel.send(embed=embed)
        
        # Log to comprehensive logging system
        if hasattr(self.bot, 'comprehensive_logger') and self.bot.comprehensive_logger:
            await self.bot.comprehensive_logger.log_citizenship_application_approved(
                application, user, interaction.user
            )

        # Send DM to applicant
        try:
            dm_embed = discord.Embed(
                title="✅ Citizenship Application Approved",
                color=0x16a085,  # Professional green
                description="**Congratulations!**\n\n"
                           "Your application for British Virgin Islands citizenship has been **officially approved**.\n\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           "You are now a **certified citizen** of the British Virgin Islands!\n\n"
                           "**Next Steps:**\n"
                           "• Your citizenship role will be assigned shortly\n"
                           "• You now have access to citizen-only channels\n"
                           "• Welcome to the BVI community!"
            )
            dm_embed.set_footer(
                text="Government of the British Virgin Islands | Department of Immigration", 
                icon_url=get_image_url("footer_icon")
            )
            dm_embed.set_thumbnail(url=get_image_url("thumbnail"))

            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent approval DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

        # Respond to the interaction
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
        
        # Log to comprehensive logging system
        if hasattr(self.bot, 'comprehensive_logger') and self.bot.comprehensive_logger:
            await self.bot.comprehensive_logger.log_citizenship_application_rejected(
                application, user, interaction.user, reason
            )

        # Send DM to applicant
        try:
            dm_embed = discord.Embed(
                title="❌ Citizenship Application Declined",
                color=0xe74c3c,  # Professional red
                description=f"**Application Status Update**\n\n"
                           f"Unfortunately, your application for British Virgin Islands citizenship has been **declined**.\n\n"
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           f"**Reason for Decline:**\n{reason}\n\n"
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           f"**Next Steps:**\n"
                           f"• You may reapply in the future if circumstances change\n"
                           f"• Contact our support team if you have questions\n"
                           f"• Review citizenship requirements before reapplying"
            )
            dm_embed.set_image(url=get_image_url("banner"))
            dm_embed.set_footer(
                text="Government of the British Virgin Islands | Department of Immigration", 
                icon_url=get_image_url("footer_icon")
            )
            dm_embed.set_thumbnail(url=get_image_url("thumbnail"))

            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent decline DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

        # Respond to the interaction
        await interaction.response.send_message(
            settings.messages.decline_success.format(user=user.mention),
            ephemeral=True
        )

