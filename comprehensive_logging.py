"""
Comprehensive logging system for the British Virgin Islands Discord Bot
Focused on citizenship application tracking only
"""
import logging
import discord
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from config import settings

logger = logging.getLogger(__name__)

class ComprehensiveLogger:
    """Handles citizenship application logging only"""

    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1397315480540151900  # Specified channel ID

    async def get_log_channel(self) -> Optional[discord.TextChannel]:
        """Get the comprehensive log channel"""
        try:
            logger.debug(f"Attempting to get log channel with ID: {self.log_channel_id}")

            # First try to get from cache
            channel = self.bot.get_channel(self.log_channel_id)

            if channel and isinstance(channel, discord.TextChannel):
                logger.debug(f"Found channel in cache: {channel.name}")
                return channel

            # If not in cache, try to fetch it
            try:
                channel = await self.bot.fetch_channel(self.log_channel_id)
                if isinstance(channel, discord.TextChannel):
                    logger.debug(f"Fetched channel from API: {channel.name}")
                    return channel
            except discord.NotFound:
                logger.error(f"Channel {self.log_channel_id} not found")
            except discord.Forbidden:
                logger.error(f"Bot lacks permission to access channel {self.log_channel_id}")
            except Exception as fetch_error:
                logger.error(f"Error fetching channel {self.log_channel_id}: {fetch_error}")

            logger.warning(f"Could not find or access log channel {self.log_channel_id}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error getting log channel: {e}")
            return None

    async def log_event(self, title: str, description: str, color: int = 0x3498db, 
                       fields: Optional[list] = None, user: Optional[discord.Member] = None):
        """Log an event to the comprehensive log channel"""
        try:
            logger.info(f"Attempting to log event: {title}")

            log_channel = await self.get_log_channel()
            if not log_channel:
                logger.error(f"Log channel {self.log_channel_id} not found or inaccessible")
                return

            logger.info(f"Found log channel: {log_channel.name} (ID: {log_channel.id})")

            # Check bot permissions in the channel
            permissions = log_channel.permissions_for(log_channel.guild.me)
            if not permissions.send_messages:
                logger.error(f"Bot lacks send_messages permission in {log_channel.name}")
                return
            if not permissions.embed_links:
                logger.error(f"Bot lacks embed_links permission in {log_channel.name}")
                return

            embed = discord.Embed(
                title=f"📋 {title}",
                description=description,
                color=color,
                timestamp=datetime.utcnow()
            )

            if user:
                try:
                    embed.set_author(
                        name=f"{user.display_name} ({user})",
                        icon_url=user.display_avatar.url if user.display_avatar else None
                    )
                except Exception as author_error:
                    logger.warning(f"Failed to set embed author: {author_error}")

            if fields:
                for i, field in enumerate(fields):
                    try:
                        # Ensure field values are strings and not too long
                        field_name = str(field.get('name', f'Field {i+1}'))[:256]
                        field_value = str(field.get('value', 'N/A'))[:1024]
                        field_inline = bool(field.get('inline', False))

                        embed.add_field(
                            name=field_name,
                            value=field_value,
                            inline=field_inline
                        )
                    except Exception as field_error:
                        logger.warning(f"Failed to add field {i}: {field_error}")

            embed.set_footer(
                text="British Virgin Islands Department of Immigration",
                icon_url="https://i.imgur.com/9K8rZtL.png"
            )

            # Ensure embed is within Discord limits
            if len(embed) > 6000:
                logger.warning("Embed too large, truncating description")
                embed.description = embed.description[:2000] + "... (truncated)"

            await log_channel.send(embed=embed)
            logger.info(f"Successfully logged event: {title}")

        except discord.HTTPException as http_error:
            logger.error(f"Discord HTTP error logging event '{title}': {http_error}")
        except discord.Forbidden:
            logger.error(f"Forbidden error - bot lacks permissions to log in channel {self.log_channel_id}")
        except Exception as e:
            logger.error(f"Unexpected error logging event '{title}': {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

    async def log_citizenship_application_submitted(self, application, user: discord.User):
        """Log detailed citizenship application submission"""
        fields = [
            {
                'name': '👤 Applicant Details',
                'value': f"**Discord:** {user.mention} ({user})\n"
                        f"**ID:** {user.id}\n"
                        f"**Account Created:** <t:{int(user.created_at.timestamp())}:F>\n"
                        f"**Roblox Username:** {application.roblox_username}",
                'inline': False
            },
            {
                'name': '📝 Application Content',
                'value': f"**Reason for Citizenship:**\n```\n{application.reason[:450]}{'...' if len(application.reason) > 450 else ''}\n```",
                'inline': False
            },
            {
                'name': '🔍 Background Check',
                'value': f"**Criminal Record:** {application.criminal_record}",
                'inline': False
            }
        ]

        if application.additional_info:
            fields.append({
                'name': '📋 Additional Information',
                'value': f"```\n{application.additional_info[:450]}{'...' if len(application.additional_info) > 450 else ''}\n```",
                'inline': False
            })

        fields.extend([
            {
                'name': '⏰ Submission Details',
                'value': f"**Submitted:** <t:{int(application.submitted_at.timestamp())}:F>\n"
                        f"**Status:** {application.status.value.upper()}\n"
                        f"**Application ID:** {application.user_id}",
                'inline': False
            },
            {
                'name': '📊 User Statistics',
                'value': f"**Server Join Date:** <t:{int(user.joined_at.timestamp()) if hasattr(user, 'joined_at') and user.joined_at else int(datetime.utcnow().timestamp())}:F>\n"
                        f"**Total Roles:** {len(user.roles) if hasattr(user, 'roles') else 'N/A'}\n"
                        f"**Is Bot:** {'Yes' if user.bot else 'No'}",
                'inline': False
            }
        ])

        await self.log_event(
            title="New Citizenship Application Submitted",
            description=f"**{user.display_name}** has submitted a new citizenship application for review.\n\n"
                       f"This application requires administrative review and approval.",
            color=0x3498db,
            fields=fields,
            user=user
        )

    async def log_citizenship_application_approved(self, application, user: discord.Member, reviewer: discord.User):
        """Log detailed citizenship application approval"""
        fields = [
            {
                'name': '✅ Approval Details',
                'value': f"**Approved By:** {reviewer.mention} ({reviewer})\n"
                        f"**Approved At:** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                        f"**Application ID:** {application.user_id}",
                'inline': False
            },
            {
                'name': '👤 New Citizen Information',
                'value': f"**Discord:** {user.mention} ({user})\n"
                        f"**Roblox Username:** {application.roblox_username}\n"
                        f"**Original Application:** <t:{int(application.submitted_at.timestamp())}:F>",
                'inline': False
            },
            {
                'name': '📝 Original Application Reason',
                'value': f"```\n{application.reason[:250]}{'...' if len(application.reason) > 250 else ''}\n```",
                'inline': False
            }
        ]

        await self.log_event(
            title="Citizenship Application APPROVED",
            description=f"🎉 **{user.display_name}** has been **APPROVED** for British Virgin Islands citizenship!\n\n"
                       f"They are now a certified citizen with full access to citizen privileges.",
            color=0x2ecc71,
            fields=fields,
            user=user
        )

    async def log_citizenship_application_rejected(self, application, user: discord.Member, reviewer: discord.User, reason: str):
        """Log detailed citizenship application rejection"""
        fields = [
            {
                'name': '❌ Rejection Details',
                'value': f"**Rejected By:** {reviewer.mention} ({reviewer})\n"
                        f"**Rejected At:** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                        f"**Application ID:** {application.user_id}",
                'inline': False
            },
            {
                'name': '📋 Rejection Reason',
                'value': reason,
                'inline': False
            },
            {
                'name': '👤 Applicant Information',
                'value': f"**Discord:** {user.mention} ({user})\n"
                        f"**Roblox Username:** {application.roblox_username}\n"
                        f"**Applied On:** <t:{int(application.submitted_at.timestamp())}:F>",
                'inline': False
            },
            {
                'name': '📝 Original Application',
                'value': f"```\n{application.reason[:250]}{'...' if len(application.reason) > 250 else ''}\n```",
                'inline': False
            }
        ]

        await self.log_event(
            title="Citizenship Application REJECTED",
            description=f"❌ **{user.display_name}**'s citizenship application has been **REJECTED**.\n\n"
                       f"The applicant has been notified and may reapply in the future.",
            color=0xe74c3c,
            fields=fields,
            user=user
        )

# Global logger instance
comprehensive_logger = None

def initialize_logger(bot):
    """Initialize the comprehensive logger"""
    global comprehensive_logger
    comprehensive_logger = ComprehensiveLogger(bot)
    return comprehensive_logger