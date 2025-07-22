"""
Discord forms and modals for the British Virgin Islands Bot
"""
import logging
import discord
from config import settings
from utils import ChannelManager, EmbedBuilder
from models import CitizenshipApplication

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
        
        # Send the modal
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
            embed = discord.Embed(
                title="📋 Your Application Status",
                color=settings.embeds.application_submitted,
                description=f"**Status:** {application.status.value.title()}\n"
                           f"**Submitted:** <t:{int(application.submitted_at.timestamp())}:R>\n"
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
            title="🏴󠁧󠁢󠁥󠁮󠁧󠁿 British Virgin Islands Citizenship",
            color=settings.embeds.application_submitted,
            description="**Benefits of BVI Citizenship:**\n"
                       "• Access to exclusive BVI community events\n"
                       "• Special citizen role and privileges\n"
                       "• Priority support and assistance\n"
                       "• Participation in BVI governance discussions\n\n"
                       "**Application Requirements:**\n"
                       "• Valid Roblox username\n"
                       "• Clear criminal record disclosure\n"
                       "• Genuine interest in the BVI community\n"
                       "• Respectful behavior and good standing"
        )
        embed.set_footer(text="Applications are reviewed by our citizenship team")
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
            title="📞 Contact Support",
            color=settings.embeds.application_submitted,
            description="Need help with your citizenship application?\n\n"
                       "**Contact Methods:**\n"
                       "• Message a staff member directly\n"
                       "• Open a support ticket\n"
                       "• Ask in the general support channel\n\n"
                       "**Common Issues:**\n"
                       "• Application not submitted - Try again\n"
                       "• Status questions - Check your DMs\n"
                       "• Technical problems - Contact an admin"
        )
        embed.set_footer(text="Our support team is here to help!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_timeout(self):
        """Handle view timeout"""
        # Disable all buttons when the view times out
        for item in self.children:
            item.disabled = True

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