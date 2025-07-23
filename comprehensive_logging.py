
"""
Comprehensive logging system for the British Virgin Islands Discord Bot
Extensive logging for all server events and citizenship applications
"""
import logging
import discord
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from config import settings

logger = logging.getLogger(__name__)

class ComprehensiveLogger:
    """Handles all comprehensive logging for the bot"""
    
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
                text="British Virgin Islands Comprehensive Log",
                icon_url="https://i.imgur.com/xqmqk9x.png"
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
    
    async def log_member_join(self, member: discord.Member):
        """Log when a member joins the server"""
        fields = [
            {
                'name': '👤 Member Information',
                'value': f"**Name:** {member.display_name}\n"
                        f"**Username:** {member}\n"
                        f"**ID:** {member.id}\n"
                        f"**Bot:** {'Yes' if member.bot else 'No'}",
                'inline': True
            },
            {
                'name': '📅 Account Details',
                'value': f"**Created:** <t:{int(member.created_at.timestamp())}:F>\n"
                        f"**Joined:** <t:{int(member.joined_at.timestamp())}:F>\n"
                        f"**Account Age:** {(datetime.utcnow() - member.created_at).days} days",
                'inline': True
            },
            {
                'name': '📊 Server Statistics',
                'value': f"**Total Members:** {len(member.guild.members)}\n"
                        f"**Member #:** {len([m for m in member.guild.members if m.joined_at <= member.joined_at])}",
                'inline': False
            }
        ]
        
        await self.log_event(
            title="Member Joined Server",
            description=f"👋 **{member.display_name}** has joined the server!",
            color=0x2ecc71,
            fields=fields,
            user=member
        )
    
    async def log_member_leave(self, member: discord.Member):
        """Log when a member leaves the server"""
        fields = [
            {
                'name': '👤 Member Information',
                'value': f"**Name:** {member.display_name}\n"
                        f"**Username:** {member}\n"
                        f"**ID:** {member.id}",
                'inline': True
            },
            {
                'name': '📅 Membership Duration',
                'value': f"**Joined:** <t:{int(member.joined_at.timestamp()) if member.joined_at else int(datetime.utcnow().timestamp())}:F>\n"
                        f"**Left:** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                        f"**Duration:** {(datetime.utcnow() - member.joined_at).days if member.joined_at else 0} days",
                'inline': True
            },
            {
                'name': '🏷️ Roles at Leave',
                'value': ', '.join([role.name for role in member.roles[1:]]) if len(member.roles) > 1 else 'No roles',
                'inline': False
            }
        ]
        
        await self.log_event(
            title="Member Left Server",
            description=f"👋 **{member.display_name}** has left the server.",
            color=0xe67e22,
            fields=fields,
            user=member
        )
    
    async def log_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log when a member is banned"""
        try:
            ban_info = await guild.fetch_ban(user)
            ban_reason = ban_info.reason or "No reason provided"
        except:
            ban_reason = "Unable to fetch ban reason"
        
        fields = [
            {
                'name': '👤 Banned User',
                'value': f"**Name:** {user.display_name}\n"
                        f"**Username:** {user}\n"
                        f"**ID:** {user.id}",
                'inline': True
            },
            {
                'name': '🔨 Ban Details',
                'value': f"**Reason:** {ban_reason}\n"
                        f"**Banned At:** <t:{int(datetime.utcnow().timestamp())}:F>",
                'inline': True
            }
        ]
        
        await self.log_event(
            title="Member Banned",
            description=f"🔨 **{user.display_name}** has been banned from the server.",
            color=0xe74c3c,
            fields=fields,
            user=user
        )
    
    async def log_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log when a member is unbanned"""
        fields = [
            {
                'name': '👤 Unbanned User',
                'value': f"**Name:** {user.display_name}\n"
                        f"**Username:** {user}\n"
                        f"**ID:** {user.id}",
                'inline': True
            },
            {
                'name': '🔓 Unban Details',
                'value': f"**Unbanned At:** <t:{int(datetime.utcnow().timestamp())}:F>",
                'inline': True
            }
        ]
        
        await self.log_event(
            title="Member Unbanned",
            description=f"🔓 **{user.display_name}** has been unbanned from the server.",
            color=0x2ecc71,
            fields=fields,
            user=user
        )
    
    async def log_message_delete(self, message: discord.Message):
        """Log when a message is deleted"""
        if message.author.bot:
            return  # Skip bot messages
        
        fields = [
            {
                'name': '👤 Author',
                'value': f"**Name:** {message.author.display_name}\n"
                        f"**Username:** {message.author}\n"
                        f"**ID:** {message.author.id}",
                'inline': True
            },
            {
                'name': '📍 Location',
                'value': f"**Channel:** {message.channel.mention}\n"
                        f"**Message ID:** {message.id}\n"
                        f"**Created:** <t:{int(message.created_at.timestamp())}:F>",
                'inline': True
            },
            {
                'name': '📝 Content',
                'value': f"```\n{message.content[:900]}{'...' if len(message.content) > 900 else ''}\n```" if message.content else '*Message contains no text content*',
                'inline': False
            }
        ]
        
        # Add attachment information
        if message.attachments:
            attachment_info = '\n'.join([f"• {att.filename} ({att.size} bytes)" for att in message.attachments])
            fields.append({
                'name': '📎 Attachments',
                'value': attachment_info[:500] + ('...' if len(attachment_info) > 500 else ''),
                'inline': False
            })
        
        # Add embed information if present
        if message.embeds:
            embed_info = []
            for i, embed in enumerate(message.embeds[:3]):  # Limit to first 3 embeds
                embed_title = embed.title or "Untitled Embed"
                embed_info.append(f"• **{embed_title}**" + (f" - {embed.description[:50]}..." if embed.description else ""))
            
            fields.append({
                'name': '🔗 Embeds',
                'value': '\n'.join(embed_info)[:500] + ('...' if len('\n'.join(embed_info)) > 500 else ''),
                'inline': False
            })
        
        await self.log_event(
            title="Message Deleted",
            description=f"🗑️ A message by **{message.author.display_name}** was deleted in {message.channel.mention}",
            color=0xe74c3c,
            fields=fields,
            user=message.author
        )
    
    async def log_message_edit(self, before: discord.Message, after: discord.Message):
        """Log when a message is edited"""
        if before.author.bot or before.content == after.content:
            return  # Skip bot messages and non-content changes
        
        fields = [
            {
                'name': '👤 Author',
                'value': f"**Name:** {before.author.display_name}\n"
                        f"**Username:** {before.author}\n"
                        f"**ID:** {before.author.id}",
                'inline': True
            },
            {
                'name': '📍 Location',
                'value': f"**Channel:** {before.channel.mention}\n"
                        f"**Message ID:** {before.id}\n"
                        f"**Edited:** <t:{int(datetime.utcnow().timestamp())}:F>",
                'inline': True
            },
            {
                'name': '📝 Before',
                'value': f"```\n{before.content[:450]}{'...' if len(before.content) > 450 else ''}\n```" if before.content else '*No text content*',
                'inline': False
            },
            {
                'name': '📝 After',
                'value': f"```\n{after.content[:450]}{'...' if len(after.content) > 450 else ''}\n```" if after.content else '*No text content*',
                'inline': False
            }
        ]
        
        await self.log_event(
            title="Message Edited",
            description=f"✏️ **{before.author.display_name}** edited a message in {before.channel.mention}",
            color=0xf39c12,
            fields=fields,
            user=before.author
        )
    
    async def log_role_create(self, role: discord.Role):
        """Log when a role is created"""
        fields = [
            {
                'name': '🏷️ Role Details',
                'value': f"**Name:** {role.name}\n"
                        f"**ID:** {role.id}\n"
                        f"**Color:** {str(role.color)}\n"
                        f"**Hoisted:** {'Yes' if role.hoist else 'No'}\n"
                        f"**Mentionable:** {'Yes' if role.mentionable else 'No'}",
                'inline': True
            },
            {
                'name': '🔐 Permissions',
                'value': f"**Administrator:** {'Yes' if role.permissions.administrator else 'No'}\n"
                        f"**Manage Server:** {'Yes' if role.permissions.manage_guild else 'No'}\n"
                        f"**Manage Roles:** {'Yes' if role.permissions.manage_roles else 'No'}\n"
                        f"**Manage Channels:** {'Yes' if role.permissions.manage_channels else 'No'}",
                'inline': True
            }
        ]
        
        await self.log_event(
            title="Role Created",
            description=f"🎭 A new role **{role.name}** was created",
            color=0x9b59b6,
            fields=fields
        )
    
    async def log_role_delete(self, role: discord.Role):
        """Log when a role is deleted"""
        fields = [
            {
                'name': '🏷️ Deleted Role',
                'value': f"**Name:** {role.name}\n"
                        f"**ID:** {role.id}\n"
                        f"**Members:** {len(role.members)}\n"
                        f"**Color:** {str(role.color)}",
                'inline': False
            }
        ]
        
        await self.log_event(
            title="Role Deleted",
            description=f"🗑️ Role **{role.name}** was deleted",
            color=0xe74c3c,
            fields=fields
        )

# Global logger instance
comprehensive_logger = None

def initialize_logger(bot):
    """Initialize the comprehensive logger"""
    global comprehensive_logger
    comprehensive_logger = ComprehensiveLogger(bot)
    return comprehensive_logger
