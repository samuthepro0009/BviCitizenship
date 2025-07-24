"""
Advanced notification system for the British Virgin Islands Discord Bot
Comprehensive messaging and alert management
"""
import logging
import discord
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from config import settings
from utils import DMManager, EmbedBuilder
from image_config import get_image_url

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications"""
    APPLICATION_RECEIVED = "application_received"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"
    APPLICATION_PENDING = "application_pending"
    SYSTEM_MAINTENANCE = "system_maintenance"
    POLICY_UPDATE = "policy_update"
    REMINDER = "reminder"
    WELCOME = "welcome"

@dataclass
class NotificationTemplate:
    """Template for notifications"""
    title: str
    description: str
    color: int
    footer_text: str
    include_thumbnail: bool = True
    include_timestamp: bool = True
    auto_delete_after: Optional[int] = None  # seconds

class NotificationManager:
    """Manages all bot notifications and announcements"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.notification_queue: List[Dict] = []
        self.scheduled_notifications: List[Dict] = []
    
    def _initialize_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        """Initialize notification templates"""
        return {
            NotificationType.APPLICATION_RECEIVED: NotificationTemplate(
                title="✅ Application Received",
                description="Your citizenship application has been successfully submitted and is now under review.",
                color=0x3498db,
                footer_text="Expected processing time: 2-5 business days",
            ),
            
            NotificationType.APPLICATION_APPROVED: NotificationTemplate(
                title="🎉 Citizenship Approved!",
                description="Congratulations! Your application for British Virgin Islands citizenship has been **APPROVED**.",
                color=0x2ecc71,
                footer_text="Welcome to the British Virgin Islands!",
            ),
            
            NotificationType.APPLICATION_REJECTED: NotificationTemplate(
                title="❌ Application Not Approved",
                description="Unfortunately, your citizenship application has been declined after careful review.",
                color=0xe74c3c,
                footer_text="You may reapply after addressing the concerns listed above.",
            ),
            
            NotificationType.WELCOME: NotificationTemplate(
                title="🏝️ Welcome to the British Virgin Islands!",
                description="Welcome to our official Discord community! We're excited to have you here.",
                color=0x1e3a8a,
                footer_text="Government of the British Virgin Islands",
            ),
            
            NotificationType.SYSTEM_MAINTENANCE: NotificationTemplate(
                title="🔧 System Maintenance Notice",
                description="The citizenship application system will undergo scheduled maintenance.",
                color=0xf39c12,
                footer_text="We apologize for any inconvenience.",
            ),
            
            NotificationType.POLICY_UPDATE: NotificationTemplate(
                title="📋 Policy Update",
                description="Important updates have been made to our citizenship policies and procedures.",
                color=0x9b59b6,
                footer_text="Please review the updated requirements.",
            ),
        }
    
    async def send_notification(self, 
                              user: discord.User, 
                              notification_type: NotificationType,
                              custom_fields: Optional[List[Dict]] = None,
                              custom_description: Optional[str] = None) -> bool:
        """Send a notification to a user"""
        try:
            template = self.templates.get(notification_type)
            if not template:
                logger.error(f"Unknown notification type: {notification_type}")
                return False
            
            # Create embed
            embed = discord.Embed(
                title=template.title,
                description=custom_description or template.description,
                color=template.color
            )
            
            if template.include_timestamp:
                embed.timestamp = discord.utils.utcnow()
            
            if template.include_thumbnail:
                embed.set_thumbnail(url=get_image_url("thumbnail"))
            
            # Add custom fields if provided
            if custom_fields:
                for field in custom_fields:
                    embed.add_field(
                        name=field.get('name', 'Information'),
                        value=field.get('value', 'N/A'),
                        inline=field.get('inline', False)
                    )
            
            embed.set_footer(
                text=template.footer_text,
                icon_url=get_image_url("footer_icon")
            )
            
            # Send DM
            success = await DMManager.send_dm_safe(user, embed)
            
            if success:
                logger.info(f"Notification sent to {user}: {notification_type.value}")
            else:
                logger.warning(f"Failed to send notification to {user}: {notification_type.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def send_bulk_notification(self, 
                                   users: List[discord.User],
                                   notification_type: NotificationType,
                                   custom_fields: Optional[List[Dict]] = None,
                                   custom_description: Optional[str] = None) -> Dict[str, int]:
        """Send notifications to multiple users"""
        results = {"success": 0, "failed": 0}
        
        for user in users:
            success = await self.send_notification(
                user, notification_type, custom_fields, custom_description
            )
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return results
    
    async def schedule_notification(self, 
                                  user: discord.User,
                                  notification_type: NotificationType,
                                  delay_hours: int,
                                  custom_fields: Optional[List[Dict]] = None) -> None:
        """Schedule a notification to be sent later"""
        send_time = datetime.now() + timedelta(hours=delay_hours)
        
        scheduled_notification = {
            "user": user,
            "notification_type": notification_type,
            "send_time": send_time,
            "custom_fields": custom_fields
        }
        
        self.scheduled_notifications.append(scheduled_notification)
        logger.info(f"Scheduled notification for {user} at {send_time}")
    
    async def process_scheduled_notifications(self) -> None:
        """Process and send scheduled notifications"""
        now = datetime.now()
        notifications_to_send = []
        
        # Find notifications ready to send
        for notification in self.scheduled_notifications[:]:
            if notification["send_time"] <= now:
                notifications_to_send.append(notification)
                self.scheduled_notifications.remove(notification)
        
        # Send ready notifications
        for notification in notifications_to_send:
            await self.send_notification(
                notification["user"],
                notification["notification_type"],
                notification.get("custom_fields")
            )
    
    async def send_welcome_message(self, member: discord.Member) -> bool:
        """Send welcome message to new server members"""
        custom_fields = [
            {
                "name": "🎯 Getting Started",
                "value": "• Read our rules and guidelines\n"
                        "• Introduce yourself in #introductions\n"
                        "• Apply for citizenship with `/citizenship`\n"
                        "• Explore our channels and community",
                "inline": False
            },
            {
                "name": "📋 Next Steps",
                "value": "Ready to become a BVI citizen? Use the `/citizenship` command to start your application process!",
                "inline": False
            }
        ]
        
        return await self.send_notification(
            member,
            NotificationType.WELCOME,
            custom_fields=custom_fields
        )

class AnnouncementSystem:
    """System for server-wide announcements"""
    
    def __init__(self):
        self.announcement_history: List[Dict] = []
    
    async def send_server_announcement(self, 
                                     guild: discord.Guild,
                                     channel_name: str,
                                     title: str,
                                     description: str,
                                     color: int = 0x1e3a8a,
                                     ping_role: Optional[str] = None) -> bool:
        """Send announcement to server channel"""
        try:
            # Find announcement channel
            channel = discord.utils.get(guild.channels, name=channel_name)
            if not channel or not isinstance(channel, discord.TextChannel):
                logger.error(f"Announcement channel '{channel_name}' not found")
                return False
            
            # Create announcement embed
            embed = discord.Embed(
                title=f"📢 {title}",
                description=description,
                color=color,
                timestamp=discord.utils.utcnow()
            )
            
            embed.set_thumbnail(url=get_image_url("thumbnail"))
            embed.set_footer(
                text="Government of the British Virgin Islands",
                icon_url=get_image_url("footer_icon")
            )
            
            # Prepare message content
            content = ""
            if ping_role:
                role = discord.utils.get(guild.roles, name=ping_role)
                if role:
                    content = f"{role.mention}"
            
            # Send announcement
            message = await channel.send(content=content, embed=embed)
            
            # Record announcement
            self.announcement_history.append({
                "title": title,
                "description": description,
                "channel": channel_name,
                "timestamp": datetime.now(),
                "message_id": message.id
            })
            
            logger.info(f"Server announcement sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending server announcement: {e}")
            return False
    
    async def send_maintenance_notice(self, 
                                    guild: discord.Guild,
                                    start_time: datetime,
                                    duration_hours: int,
                                    affected_systems: List[str]) -> bool:
        """Send maintenance notice to server"""
        description = (
            f"**Scheduled Maintenance Window**\n\n"
            f"🕐 **Start Time:** <t:{int(start_time.timestamp())}:F>\n"
            f"⏱️ **Duration:** {duration_hours} hours\n"
            f"🔧 **Affected Systems:**\n"
        )
        
        for system in affected_systems:
            description += f"• {system}\n"
        
        description += (
            f"\n**What to Expect:**\n"
            f"• Temporary service interruptions\n"
            f"• Application submissions may be delayed\n"
            f"• Some features may be unavailable\n\n"
            f"We apologize for any inconvenience and appreciate your patience."
        )
        
        return await self.send_server_announcement(
            guild=guild,
            channel_name="announcements",
            title="System Maintenance Notice",
            description=description,
            color=0xf39c12,
            ping_role="citizens"
        )
    
    async def send_policy_update(self, 
                               guild: discord.Guild,
                               update_summary: str,
                               effective_date: datetime,
                               changes: List[str]) -> bool:
        """Send policy update announcement"""
        description = (
            f"**Important Policy Updates**\n\n"
            f"📅 **Effective Date:** <t:{int(effective_date.timestamp())}:D>\n\n"
            f"**Summary:** {update_summary}\n\n"
            f"**Key Changes:**\n"
        )
        
        for change in changes:
            description += f"• {change}\n"
        
        description += (
            f"\n**Action Required:**\n"
            f"• Review the updated policies\n"
            f"• Ensure compliance with new requirements\n"
            f"• Contact support if you have questions\n\n"
            f"Full policy documentation is available in #rules-and-policies."
        )
        
        return await self.send_server_announcement(
            guild=guild,
            channel_name="announcements",
            title="Policy Update",
            description=description,
            color=0x9b59b6,
            ping_role="citizens"
        )

# Global notification manager instance
notification_manager = NotificationManager()
announcement_system = AnnouncementSystem()