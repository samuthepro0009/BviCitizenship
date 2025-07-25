"""Fixing docstring format and image URLs."""
import logging
import discord
from config import settings
from utils import ChannelManager, EmbedBuilder
from models import CitizenshipApplication
from image_config import get_image_url

logger = logging.getLogger(__name__)

class CitizenshipDashboard(discord.ui.View):
    """Interactive dashboard for citizenship services"""

    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout

    @discord.ui.button(
        label='Apply for Citizenship',
        emoji='📋',
        style=discord.ButtonStyle.primary,
        custom_id='apply_citizenship'
    )
    async def apply_citizenship(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle citizenship application button"""
        # Check if user already has a pending application
        bot = interaction.client
        if hasattr(bot, 'pending_applications') and interaction.user.id in bot.pending_applications:
            await interaction.response.send_message(
                settings.messages.application_exists,
                ephemeral=True
            )
            return

        # Send the citizenship modal
        modal = CitizenshipModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label='Check Application Status',
        emoji='🔍',
        style=discord.ButtonStyle.secondary,
        custom_id='check_status'
    )
    async def check_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle status check button"""
        bot = interaction.client
        if hasattr(bot, 'pending_applications') and interaction.user.id in bot.pending_applications:
            application = bot.pending_applications[interaction.user.id]
            # Handle submitted_at attribute for backward compatibility
            submitted_time = "Recently"
            if hasattr(application, 'submitted_at') and application.submitted_at:
                submitted_time = f"<t:{int(application.submitted_at.timestamp())}:R>"

            embed = discord.Embed(
                title="📋 Your Application Status",
                color=settings.embeds.application_submitted,
                description=f"**Status:** {application.status.value.title()}\n"
                           f"**Submitted:** {submitted_time}\n"
                           f"**Roblox Username:** {application.roblox_username}"
            )
            embed.set_footer(text="You will receive a DM when your application is reviewed.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="📋 Application Status",
                color=settings.embeds.error_color,
                description="You don't have any pending citizenship applications.\n"
                           "Click 'Apply for Citizenship' to submit your application!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label='Citizenship Information',
        emoji='ℹ️',
        style=discord.ButtonStyle.secondary,
        custom_id='citizenship_info'
    )
    async def citizenship_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle information button"""
        embed = discord.Embed(
            title="British Virgin Islands Citizenship Information",
            color=0x1e3a8a,  # Professional navy blue
            description="**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
                       "**🎯 Benefits of BVI Citizenship:**\n"
                       "• Access to exclusive BVI community events\n"
                       "• Special citizen role and privileges\n"
                       "• Priority support and assistance\n"
                       "• Participation in BVI governance discussions\n"
                       "• Access to citizen-only channels and content\n\n"
                       "**📋 Application Requirements:**\n"
                       "• Valid Roblox username\n"
                       "• Clear criminal record disclosure\n"
                       "• Genuine interest in the BVI community\n"
                       "• Respectful behavior and good standing\n"
                       "• Completion of all required forms\n\n"
                       "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
        )
        embed.set_footer(
            text="Government of the British Virgin Islands | Citizenship Department", 
            icon_url=get_image_url("footer_icon")
        )
        embed.set_thumbnail(url=get_image_url("thumbnail"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label='Contact Support',
        emoji='📞',
        style=discord.ButtonStyle.secondary,
        custom_id='contact_support'
    )
    async def contact_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle support contact button"""
        embed = discord.Embed(
            title="📞 Citizenship Support Services",
            color=0x1e3a8a,  # Professional navy blue
            description="**Need assistance with your citizenship application?**\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                       "**📧 Contact Methods:**\n"
                       "• Message a certified staff member directly\n"
                       "• Open an official support ticket\n"
                       "• Ask in the designated support channel\n"
                       "• Email our citizenship department\n\n"
                       "**🔧 Common Issues & Solutions:**\n"
                       "• Application not submitted → Try submitting again\n"
                       "• Status questions → Check your direct messages\n"
                       "• Technical problems → Contact a system administrator\n"
                       "• Form errors → Ensure all fields are completed\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        embed.set_footer(
            text="Government of the British Virgin Islands | Citizenship Department", 
            icon_url=get_image_url("footer_icon")
        )
        embed.set_thumbnail(url=get_image_url("thumbnail"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_timeout(self):
        """Handle view timeout"""
        # Disable all buttons when the view times out
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True

class CitizenshipModal(discord.ui.Modal):
    """Single-page citizenship application form"""

    def __init__(self):
        super().__init__(title='BVI Citizenship Application')

        # Simplified form with 4 fields (Discord allows up to 5)
        self.roblox_username = discord.ui.TextInput(
            label="Roblox Username",
            placeholder="Enter your Roblox username...",
            required=True,
            max_length=50
        )

        self.reason = discord.ui.TextInput(
            label="Why do you want BVI citizenship?",
            style=discord.TextStyle.paragraph,
            placeholder="Please explain your motivation...",
            required=True,
            max_length=1000
        )

        self.criminal_record = discord.ui.TextInput(
            label="Criminal Record Disclosure",
            placeholder="Yes/No and details if applicable...",
            required=True,
            max_length=500
        )

        self.additional_info = discord.ui.TextInput(
            label="Additional Information (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Any additional information...",
            required=False,
            max_length=500
        )

        # Add all components to the modal
        self.add_item(self.roblox_username)
        self.add_item(self.reason)
        self.add_item(self.criminal_record)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission"""
        try:
            # Respond immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)

            # Create application object
            application = CitizenshipApplication(
                user_id=interaction.user.id,
                user_name=str(interaction.user),
                roblox_username=self.roblox_username.value,
                discord_username=str(interaction.user),
                reason=self.reason.value,
                criminal_record=self.criminal_record.value,
                additional_info=self.additional_info.value if self.additional_info.value else ""
            )

            # Get the bot instance to access pending applications
            bot = interaction.client
            if hasattr(bot, 'pending_applications'):
                bot.pending_applications[interaction.user.id] = application

            # Log to citizenship-log channel
            if interaction.guild:
                log_channel = ChannelManager.get_citizenship_log_channel(interaction.guild)
                if log_channel:
                    embed = EmbedBuilder.create_application_embed(application, interaction.user)
                    await log_channel.send(embed=embed)

            # Log to comprehensive logging system
            bot = interaction.client
            if hasattr(bot, 'comprehensive_logger') and bot.comprehensive_logger:
                await bot.comprehensive_logger.log_citizenship_application_submitted(
                    application, interaction.user
                )

            logger.info(f"New citizenship application submitted by {interaction.user} (ID: {interaction.user.id})")

            # Send success message using followup
            await interaction.followup.send(
                settings.messages.application_success,
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error submitting citizenship application: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while submitting your application. Please try again.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while submitting your application. Please try again.",
                    ephemeral=True
                )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle modal errors"""
        logger.error(f"Modal error: {error}")

        # Try to respond if we haven't already
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ An error occurred while processing your application. Please try again later.",
                ephemeral=True
            )