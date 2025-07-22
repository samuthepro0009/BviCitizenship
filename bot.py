import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional
from models import CitizenshipApplication, ApplicationStatus
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitizenshipModal(discord.ui.Modal, title='BVI Citizenship Application'):
    def __init__(self):
        super().__init__()

    roblox_username = discord.ui.TextInput(
        label='What is your Roblox username?',
        placeholder='Enter your Roblox username...',
        required=True,
        max_length=50
    )

    discord_username = discord.ui.TextInput(
        label='What is your Discord username?',
        placeholder='Enter your Discord username...',
        required=True,
        max_length=50
    )

    reason = discord.ui.TextInput(
        label='Why do you want to become a BVI citizen?',
        style=discord.TextStyle.paragraph,
        placeholder='Please explain your motivation...',
        required=True,
        max_length=1000
    )

    criminal_record = discord.ui.TextInput(
        label='Have you been convicted of any crimes?',
        placeholder='Yes/No and details if applicable...',
        required=True,
        max_length=500
    )

    additional_info = discord.ui.TextInput(
        label='Any additional information?',
        style=discord.TextStyle.paragraph,
        placeholder='Optional additional information...',
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
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
        log_channel = discord.utils.get(interaction.guild.channels, name='citizenship-log')
        
        if log_channel:
            embed = discord.Embed(
                title="New Citizenship Application",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Applicant", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
            embed.add_field(name="Roblox Username", value=application.roblox_username, inline=True)
            embed.add_field(name="Discord Username", value=application.discord_username, inline=True)
            embed.add_field(name="Reason", value=application.reason[:500] + ("..." if len(application.reason) > 500 else ""), inline=False)
            embed.add_field(name="Criminal Record", value=application.criminal_record, inline=False)
            if application.additional_info:
                embed.add_field(name="Additional Info", value=application.additional_info[:500] + ("..." if len(application.additional_info) > 500 else ""), inline=False)
            embed.set_footer(text=f"Application ID: {application.user_id}")

            await log_channel.send(embed=embed)
        else:
            logger.warning("citizenship-log channel not found")

        await interaction.response.send_message(
            "✅ Your citizenship application has been submitted successfully! "
            "You will receive a DM once your application has been reviewed.",
            ephemeral=True
        )

class BVIBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Only use default intents to avoid privileged intent errors
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Store pending applications in memory
        self.pending_applications = {}
        
        # Admin role ID - should be set manually in production
        self.admin_role_id = int(os.getenv('ADMIN_ROLE_ID', '0'))
        
        # Roblox API settings
        self.roblox_api_key = os.getenv('ROBLOX_API_KEY', 'placeholder_key')

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    def has_admin_role(self, member: discord.Member) -> bool:
        """Check if member has the required admin role"""
        if self.admin_role_id == 0:
            logger.warning("Admin role ID not configured")
            return False
        
        return any(role.id == self.admin_role_id for role in member.roles)

# Set up the command tree with global commands
async def citizenship(interaction: discord.Interaction):
    """Open citizenship application form"""
    bot = interaction.client
    
    # Check if user already has a pending application
    if interaction.user.id in bot.pending_applications:
        await interaction.response.send_message(
            "❌ You already have a pending citizenship application. Please wait for it to be processed.",
            ephemeral=True
        )
        return

    # Send the modal
    modal = CitizenshipModal()
    await interaction.response.send_modal(modal)

async def citizenship_accept(interaction: discord.Interaction, user: discord.Member):
    """Accept a citizenship application"""
    bot = interaction.client
    
    # Check admin permissions
    if not bot.has_admin_role(interaction.user):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    # Check if application exists
    if user.id not in bot.pending_applications:
        await interaction.response.send_message(
            f"❌ No pending application found for {user.mention}.",
            ephemeral=True
        )
        return

    application = bot.pending_applications[user.id]
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by = str(interaction.user)

    # Remove from pending
    del bot.pending_applications[user.id]

    # Post to citizenship-status channel
    status_channel = discord.utils.get(interaction.guild.channels, name='citizenship-status')
    
    if status_channel:
        embed = discord.Embed(
            title="✅ Citizenship Application Approved",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Applicant", value=f"{user.mention}", inline=True)
        embed.add_field(name="Reviewed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Roblox Username", value=application.roblox_username, inline=True)
        embed.set_footer(text="Welcome to the British Virgin Islands!")

        await status_channel.send(embed=embed)

    # Send DM to applicant
    try:
        dm_embed = discord.Embed(
            title="🎉 Citizenship Application Approved!",
            description="Congratulations! Your application for British Virgin Islands citizenship has been approved.",
            color=discord.Color.green()
        )
        dm_embed.add_field(name="What's Next?", value="You are now officially a citizen of the British Virgin Islands!", inline=False)
        
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        logger.warning(f"Could not send DM to {user}")

    await interaction.response.send_message(
        f"✅ Successfully approved citizenship application for {user.mention}",
        ephemeral=True
    )

async def citizenship_decline(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Decline a citizenship application"""
    bot = interaction.client
    
    # Check admin permissions
    if not bot.has_admin_role(interaction.user):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    # Check if application exists
    if user.id not in bot.pending_applications:
        await interaction.response.send_message(
            f"❌ No pending application found for {user.mention}.",
            ephemeral=True
        )
        return

    application = bot.pending_applications[user.id]
    application.status = ApplicationStatus.REJECTED
    application.reviewed_by = str(interaction.user)
    application.rejection_reason = reason

    # Remove from pending
    del bot.pending_applications[user.id]

    # Post to citizenship-status channel
    status_channel = discord.utils.get(interaction.guild.channels, name='citizenship-status')
    
    if status_channel:
        embed = discord.Embed(
            title="❌ Citizenship Application Declined",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Applicant", value=f"{user.mention}", inline=True)
        embed.add_field(name="Reviewed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await status_channel.send(embed=embed)

    # Send DM to applicant
    try:
        dm_embed = discord.Embed(
            title="❌ Citizenship Application Declined",
            description="Unfortunately, your application for British Virgin Islands citizenship has been declined.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Next Steps", value="You may reapply in the future if circumstances change.", inline=False)
        
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        logger.warning(f"Could not send DM to {user}")

    await interaction.response.send_message(
        f"✅ Successfully declined citizenship application for {user.mention}",
        ephemeral=True
    )

async def ban(interaction: discord.Interaction, user: discord.Member, place_id: str, reason: str = "No reason provided"):
    """Ban a user from a specified Roblox place"""
    bot = interaction.client
    
    # Check admin permissions
    if not bot.has_admin_role(interaction.user):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # Get user's Roblox username from their application or profile
        roblox_username = None
        
        # Check if user has a citizenship application with Roblox username
        for app in [app for app in bot.pending_applications.values() if app.user_id == user.id]:
            roblox_username = app.roblox_username
            break

        if not roblox_username:
            await interaction.followup.send(
                f"❌ Could not find Roblox username for {user.mention}. "
                "Make sure they have submitted a citizenship application with their Roblox username.",
                ephemeral=True
            )
            return

        # Placeholder for Roblox API integration
        # In a real implementation, you would make an API call to Roblox
        success = await ban_from_roblox_place(roblox_username, place_id, reason)

        if success:
            embed = discord.Embed(
                title="🔨 Roblox Ban Executed",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Discord User", value=user.mention, inline=True)
            embed.add_field(name="Roblox Username", value=roblox_username, inline=True)
            embed.add_field(name="Place ID", value=place_id, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Banned by", value=interaction.user.mention, inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Optionally log to a moderation channel
            log_channel = discord.utils.get(interaction.guild.channels, name='mod-log')
            if log_channel:
                await log_channel.send(embed=embed)

        else:
            await interaction.followup.send(
                "❌ Failed to ban user from Roblox place. Please check the place ID and try again.",
                ephemeral=True
            )

    except Exception as e:
        logger.error(f"Error in ban command: {e}")
        await interaction.followup.send(
            "❌ An error occurred while processing the ban command.",
            ephemeral=True
        )

async def ban_from_roblox_place(roblox_username: str, place_id: str, reason: str) -> bool:
    """
    Placeholder function for Roblox API integration
    In a real implementation, this would make API calls to Roblox
    """
    try:
        # Placeholder implementation - replace with actual Roblox API calls
        logger.info(f"Attempting to ban {roblox_username} from place {place_id} for: {reason}")
        
        # Example of what a real implementation might look like:
        # headers = {'Authorization': f'Bearer {self.roblox_api_key}'}
        # data = {
        #     'username': roblox_username,
        #     'place_id': place_id,
        #     'reason': reason
        # }
        # response = requests.post('https://api.roblox.com/v1/bans', headers=headers, json=data)
        # return response.status_code == 200
        
        # For now, simulate success
        await asyncio.sleep(1)  # Simulate API delay
        return True
        
    except Exception as e:
        logger.error(f"Error banning from Roblox: {e}")
        return False

# Create the bot instance
bot = BVIBot()

# Add commands to the tree
@bot.tree.command(name="citizenship", description="Apply for British Virgin Islands citizenship")
async def citizenship_command(interaction: discord.Interaction):
    await citizenship(interaction)

@bot.tree.command(name="citizenship_accept", description="Accept a citizenship application")
@app_commands.describe(user="The user whose application to accept")
async def citizenship_accept_command(interaction: discord.Interaction, user: discord.Member):
    await citizenship_accept(interaction, user)

@bot.tree.command(name="citizenship_decline", description="Decline a citizenship application")
@app_commands.describe(
    user="The user whose application to decline",
    reason="Reason for declining the application"
)
async def citizenship_decline_command(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await citizenship_decline(interaction, user, reason)

@bot.tree.command(name="ban", description="Ban a user from a Roblox place")
@app_commands.describe(
    user="The Discord user to ban",
    place_id="The Roblox place ID to ban from", 
    reason="Reason for the ban"
)
async def ban_command(interaction: discord.Interaction, user: discord.Member, place_id: str, reason: str = "No reason provided"):
    await ban(interaction, user, place_id, reason)

def run_bot():
    """Run the bot with the Discord token"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        return
    
    bot.run(token)

if __name__ == "__main__":
    run_bot()