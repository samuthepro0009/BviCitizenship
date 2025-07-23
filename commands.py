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

            # Set the professional banner image
            embed.set_image(url="https://cdn.discordapp.com/attachments/820212786814648330/1397367721083011165/New_Project190.png?ex=6881779a&is=6880261a&hm=f3c92d05530ad093add2524d1b4ff4116237a92ea4e95ac5a16f1c684d15ab49&")

            # Set the footer with the BVI icon
            embed.set_footer(
                text="Government of the British Virgin Islands | Citizenship Department", 
                icon_url="https://cdn.discordapp.com/attachments/820212786814648330/1397367721506766869/New_Project1493.png?ex=6881779a&is=6880261a&hm=d298623ddb29b5332312806bd964f98320ba1f5d8097f24bad291e72384c7755&"
            )

            # Add thumbnail for additional branding
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/820212786814648330/1397367721506766869/New_Project1493.png?ex=6881779a&is=6880261a&hm=d298623ddb29b5332312806bd964f98320ba1f5d8097f24bad291e72384c7755&")

            # Create the interactive dashboard
            dashboard = CitizenshipDashboard()

            # Send the embed with the interactive buttons using response
            await interaction.response.send_message(
                embed=embed, 
                view=dashboard, 
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Error in citizenship application command: {e}")
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
                text="Government of the British Virgin Islands | Citizenship Department", 
                icon_url="https://i.imgur.com/CrYmk02.png"
            )
            dm_embed.set_thumbnail(url="https://i.imgur.com/CrYmk02.png")

            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent approval DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

        # Use followup since we're not deferring this command
        try:
            await interaction.response.send_message(
                settings.messages.approval_success.format(user=user.mention),
                ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
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
            dm_embed.set_footer(
                text="Government of the British Virgin Islands | Citizenship Department", 
                icon_url="https://i.imgur.com/CrYmk02.png"
            )
            dm_embed.set_thumbnail(url="https://i.imgur.com/CrYmk02.png")

            await user.send(embed=dm_embed)
            logger.info(f"Successfully sent decline DM to {user}")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user} - DMs may be disabled")
        except Exception as e:
            logger.error(f"Error sending DM to {user}: {e}")

        # Use followup if response already processed, otherwise use response
        try:
            await interaction.response.send_message(
                settings.messages.decline_success.format(user=user.mention),
                ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
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