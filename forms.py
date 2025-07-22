"""
Discord forms and modals for the British Virgin Islands Bot
"""
import logging
import discord
from config import settings
from utils import ChannelManager, EmbedBuilder
from models import CitizenshipApplication

logger = logging.getLogger(__name__)

class CitizenshipModal(discord.ui.Modal, title='BVI Citizenship Application'):
    """Modal form for citizenship applications"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize form fields with settings
        self.roblox_username = discord.ui.TextInput(
            label=settings.forms.roblox_username_label,
            placeholder=settings.forms.roblox_username_placeholder,
            required=True,
            max_length=settings.forms.roblox_username_max_length
        )
        
        self.discord_username = discord.ui.TextInput(
            label=settings.forms.discord_username_label,
            placeholder=settings.forms.discord_username_placeholder,
            required=True,
            max_length=settings.forms.discord_username_max_length
        )
        
        self.reason = discord.ui.TextInput(
            label=settings.forms.reason_label,
            style=discord.TextStyle.paragraph,
            placeholder=settings.forms.reason_placeholder,
            required=True,
            max_length=settings.forms.reason_max_length
        )
        
        self.criminal_record = discord.ui.TextInput(
            label=settings.forms.criminal_record_label,
            placeholder=settings.forms.criminal_record_placeholder,
            required=True,
            max_length=settings.forms.criminal_record_max_length
        )
        
        self.additional_info = discord.ui.TextInput(
            label=settings.forms.additional_info_label,
            style=discord.TextStyle.paragraph,
            placeholder=settings.forms.additional_info_placeholder,
            required=False,
            max_length=settings.forms.additional_info_max_length
        )

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission"""
        try:
            # Create application object
            application = CitizenshipApplication(
                user_id=interaction.user.id,
                user_name=str(interaction.user),
                roblox_username=self.roblox_username.value,
                discord_username=self.discord_username.value,
                reason=self.reason.value,
                criminal_record=self.criminal_record.value,
                additional_info=self.additional_info.value
            )

            # Get the bot instance to access pending applications
            bot = interaction.client
            bot.pending_applications[interaction.user.id] = application

            # Log to citizenship-log channel
            log_channel = ChannelManager.get_citizenship_log_channel(interaction.guild)
            
            if log_channel:
                embed = EmbedBuilder.create_application_embed(application, interaction.user)
                await log_channel.send(embed=embed)
            else:
                logger.warning(f"Channel '{settings.channels.citizenship_log}' not found")

            # Send success response
            await interaction.response.send_message(
                settings.messages.application_success,
                ephemeral=True
            )
            
            logger.info(f"New citizenship application submitted by {interaction.user} (ID: {interaction.user.id})")

        except Exception as e:
            logger.error(f"Error processing citizenship application: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing your application. Please try again later.",
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