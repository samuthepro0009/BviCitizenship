"""
Advanced features for the British Virgin Islands Discord Bot
Comprehensive enhancements for a full-featured citizenship management system
"""
import logging
import discord
from discord import app_commands
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from models import CitizenshipApplication, ApplicationStatus
from config import settings

logger = logging.getLogger(__name__)

class StatisticsType(Enum):
    """Types of statistics available"""
    APPLICATIONS = "applications"
    APPROVALS = "approvals"
    REJECTIONS = "rejections"
    PENDING = "pending"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class ApplicationStatistics:
    """Statistics for citizenship applications"""
    total_applications: int = 0
    pending_applications: int = 0
    approved_applications: int = 0
    rejected_applications: int = 0
    daily_applications: int = 0
    weekly_applications: int = 0
    monthly_applications: int = 0
    average_processing_time: float = 0.0
    approval_rate: float = 0.0
    rejection_rate: float = 0.0
    
    def __post_init__(self):
        """Calculate derived statistics"""
        total_processed = self.approved_applications + self.rejected_applications
        if total_processed > 0:
            self.approval_rate = (self.approved_applications / total_processed) * 100
            self.rejection_rate = (self.rejected_applications / total_processed) * 100

@dataclass
class UserActivity:
    """Track user activity and engagement"""
    user_id: int
    username: str
    application_count: int = 0
    last_application: Optional[datetime] = None
    status_checks: int = 0
    last_status_check: Optional[datetime] = None
    support_contacts: int = 0
    last_support_contact: Optional[datetime] = None
    citizenship_granted: bool = False
    citizenship_date: Optional[datetime] = None

class ApplicationTracker:
    """Advanced application tracking and analytics"""
    
    def __init__(self):
        self.applications_history: List[CitizenshipApplication] = []
        self.user_activities: Dict[int, UserActivity] = {}
        self.daily_stats: Dict[str, int] = {}
        
    def add_application(self, application: CitizenshipApplication):
        """Add application to tracking history"""
        self.applications_history.append(application)
        
        # Update user activity
        user_id = application.user_id
        if user_id not in self.user_activities:
            self.user_activities[user_id] = UserActivity(
                user_id=user_id,
                username=application.user_name
            )
        
        activity = self.user_activities[user_id]
        activity.application_count += 1
        activity.last_application = application.submitted_at
        
        # Update daily stats
        date_key = application.submitted_at.strftime("%Y-%m-%d")
        self.daily_stats[date_key] = self.daily_stats.get(date_key, 0) + 1
    
    def record_status_check(self, user_id: int, username: str):
        """Record when user checks their application status"""
        if user_id not in self.user_activities:
            self.user_activities[user_id] = UserActivity(
                user_id=user_id,
                username=username
            )
        
        activity = self.user_activities[user_id]
        activity.status_checks += 1
        activity.last_status_check = datetime.now()
    
    def record_support_contact(self, user_id: int, username: str):
        """Record when user contacts support"""
        if user_id not in self.user_activities:
            self.user_activities[user_id] = UserActivity(
                user_id=user_id,
                username=username
            )
        
        activity = self.user_activities[user_id]
        activity.support_contacts += 1
        activity.last_support_contact = datetime.now()
    
    def record_citizenship_granted(self, user_id: int, username: str):
        """Record when citizenship is granted to user"""
        if user_id not in self.user_activities:
            self.user_activities[user_id] = UserActivity(
                user_id=user_id,
                username=username
            )
        
        activity = self.user_activities[user_id]
        activity.citizenship_granted = True
        activity.citizenship_date = datetime.now()
    
    def get_statistics(self) -> ApplicationStatistics:
        """Generate comprehensive statistics"""
        now = datetime.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        total = len(self.applications_history)
        pending = sum(1 for app in self.applications_history if app.status == ApplicationStatus.PENDING)
        approved = sum(1 for app in self.applications_history if app.status == ApplicationStatus.APPROVED)
        rejected = sum(1 for app in self.applications_history if app.status == ApplicationStatus.REJECTED)
        
        daily = sum(1 for app in self.applications_history if app.submitted_at.date() == today)
        weekly = sum(1 for app in self.applications_history if app.submitted_at >= week_ago)
        monthly = sum(1 for app in self.applications_history if app.submitted_at >= month_ago)
        
        # Calculate average processing time for completed applications
        processed_apps = [app for app in self.applications_history if app.status != ApplicationStatus.PENDING]
        avg_processing = 0.0
        if processed_apps:
            # Simplified calculation - in real system would track actual processing times
            avg_processing = 2.5  # days (placeholder)
        
        return ApplicationStatistics(
            total_applications=total,
            pending_applications=pending,
            approved_applications=approved,
            rejected_applications=rejected,
            daily_applications=daily,
            weekly_applications=weekly,
            monthly_applications=monthly,
            average_processing_time=avg_processing
        )

class EnhancedCitizenshipDashboard(discord.ui.View):
    """Enhanced citizenship dashboard with advanced features"""
    
    def __init__(self, application_tracker: ApplicationTracker):
        super().__init__(timeout=600)  # 10 minute timeout
        self.application_tracker = application_tracker
    
    @discord.ui.button(
        label='Apply for Citizenship',
        emoji='📋',
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def apply_citizenship(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle citizenship application button"""
        bot = interaction.client
        if hasattr(bot, 'pending_applications') and interaction.user.id in bot.pending_applications:
            await interaction.response.send_message(
                settings.messages.application_exists,
                ephemeral=True
            )
            return
        
        from forms import CitizenshipModal
        modal = CitizenshipModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label='Check Status',
        emoji='🔍',
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def check_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Enhanced status checking with detailed information"""
        self.application_tracker.record_status_check(interaction.user.id, str(interaction.user))
        
        bot = interaction.client
        if hasattr(bot, 'pending_applications') and interaction.user.id in bot.pending_applications:
            application = bot.pending_applications[interaction.user.id]
            
            # Enhanced status embed with more details
            embed = discord.Embed(
                title="📋 Detailed Application Status",
                color=0x3498db,
                timestamp=discord.utils.utcnow()
            )
            
            # Status indicator with emoji
            status_emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
            embed.add_field(
                name="Current Status",
                value=f"{status_emoji.get(application.status.value, '❓')} **{application.status.value.title()}**",
                inline=True
            )
            
            embed.add_field(
                name="Application ID",
                value=f"`{application.user_id}`",
                inline=True
            )
            
            embed.add_field(
                name="Submitted",
                value=f"<t:{int(application.submitted_at.timestamp())}:R>",
                inline=True
            )
            
            embed.add_field(
                name="Roblox Username",
                value=application.roblox_username,
                inline=True
            )
            
            if application.status == ApplicationStatus.PENDING:
                embed.add_field(
                    name="Estimated Processing Time",
                    value="2-5 business days",
                    inline=True
                )
                embed.add_field(
                    name="Next Steps",
                    value="Your application is being reviewed by our citizenship team.",
                    inline=False
                )
            
            embed.set_footer(
                text="Government of the British Virgin Islands | Citizenship Department",
                icon_url="https://i.imgur.com/xqmqk9x.png"
            )
            embed.set_thumbnail(url="https://i.imgur.com/xqmqk9x.png")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # Enhanced no application found message
            embed = discord.Embed(
                title="📋 Application Status",
                color=settings.embeds.error_color,
                description="**No Application Found**\n\n"
                           "You don't have any citizenship applications on file.\n"
                           "Ready to become a BVI citizen?"
            )
            embed.add_field(
                name="Next Steps",
                value="• Click **Apply for Citizenship** below\n"
                      "• Complete the application form\n"
                      "• Wait for review (2-5 business days)\n"
                      "• Receive citizenship upon approval!",
                inline=False
            )
            embed.set_footer(
                text="Government of the British Virgin Islands | Citizenship Department",
                icon_url="https://i.imgur.com/xqmqk9x.png"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label='Application Guide',
        emoji='📖',
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def application_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Comprehensive application guide"""
        embed = discord.Embed(
            title="📖 Complete Citizenship Application Guide",
            color=0x2c3e50,
            description="**Everything you need to know about BVI citizenship**"
        )
        
        embed.add_field(
            name="🎯 Eligibility Requirements",
            value="• Must be 13+ years old\n"
                  "• Valid Roblox account required\n"
                  "• Clean criminal record\n"
                  "• Demonstrate genuine interest in BVI\n"
                  "• Respectful community behavior",
            inline=False
        )
        
        embed.add_field(
            name="📝 Application Process",
            value="**Step 1:** Click 'Apply for Citizenship'\n"
                  "**Step 2:** Complete all required fields\n"
                  "**Step 3:** Submit your application\n"
                  "**Step 4:** Wait for review (2-5 days)\n"
                  "**Step 5:** Receive decision via DM",
            inline=False
        )
        
        embed.add_field(
            name="✅ Benefits of Citizenship",
            value="• Exclusive citizen role and badge\n"
                  "• Access to citizen-only channels\n"
                  "• Priority in community events\n"
                  "• Voting rights in governance\n"
                  "• Special privileges and perks",
            inline=False
        )
        
        embed.add_field(
            name="📋 Required Information",
            value="• **Roblox Username** - Your exact Roblox username\n"
                  "• **Motivation** - Why you want citizenship\n"
                  "• **Criminal Record** - Honest disclosure required\n"
                  "• **Additional Info** - Any relevant details",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Important Notes",
            value="• All information must be truthful\n"
                  "• Fake applications will be rejected\n"
                  "• You can only have one pending application\n"
                  "• Decisions are final but you may reapply later",
            inline=False
        )
        
        embed.set_footer(
            text="Government of the British Virgin Islands | Citizenship Department",
            icon_url="https://i.imgur.com/xqmqk9x.png"
        )
        embed.set_thumbnail(url="https://i.imgur.com/xqmqk9x.png")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label='Support Center',
        emoji='🎧',
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def support_center(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Enhanced support center with FAQ and contact options"""
        self.application_tracker.record_support_contact(interaction.user.id, str(interaction.user))
        
        embed = discord.Embed(
            title="🎧 Citizenship Support Center",
            color=0x9b59b6,
            description="**Get help with your citizenship application**"
        )
        
        embed.add_field(
            name="❓ Frequently Asked Questions",
            value="**Q: How long does processing take?**\n"
                  "A: Applications are reviewed within 2-5 business days.\n\n"
                  "**Q: Can I edit my application after submission?**\n"
                  "A: No, but you can contact support for corrections.\n\n"
                  "**Q: What if my application is rejected?**\n"
                  "A: You'll receive detailed feedback and can reapply later.\n\n"
                  "**Q: Do I need to be active in the server?**\n"
                  "A: Activity helps, but it's not a strict requirement.",
            inline=False
        )
        
        embed.add_field(
            name="📞 Contact Support",
            value="• **Direct Message:** Contact any staff member\n"
                  "• **Support Channel:** #general-support\n"
                  "• **Ticket System:** React below to create a ticket\n"
                  "• **Email:** citizenship@bvi-discord.gov\n"
                  "• **Emergency:** @Admin or @Citizenship Manager",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Technical Issues",
            value="• **Form not submitting:** Try refreshing Discord\n"
                  "• **Can't see buttons:** Update Discord app\n"
                  "• **Missing DM:** Check blocked users list\n"
                  "• **Other issues:** Contact technical support",
            inline=False
        )
        
        embed.set_footer(
            text="Government of the British Virgin Islands | Citizenship Department",
            icon_url="https://i.imgur.com/xqmqk9x.png"
        )
        embed.set_thumbnail(url="https://i.imgur.com/xqmqk9x.png")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label='Statistics',
        emoji='📊',
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def view_statistics(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View public citizenship statistics"""
        stats = self.application_tracker.get_statistics()
        
        embed = discord.Embed(
            title="📊 BVI Citizenship Statistics",
            color=0x1abc9c,
            description="**Current citizenship program metrics**",
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="📈 Application Overview",
            value=f"**Total Applications:** {stats.total_applications}\n"
                  f"**Pending Review:** {stats.pending_applications}\n"
                  f"**Approved:** {stats.approved_applications}\n"
                  f"**Rejected:** {stats.rejected_applications}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Recent Activity",
            value=f"**Today:** {stats.daily_applications} applications\n"
                  f"**This Week:** {stats.weekly_applications} applications\n"
                  f"**This Month:** {stats.monthly_applications} applications\n"
                  f"**Avg. Processing:** {stats.average_processing_time} days",
            inline=True
        )
        
        embed.add_field(
            name="✅ Success Rates",
            value=f"**Approval Rate:** {stats.approval_rate:.1f}%\n"
                  f"**Rejection Rate:** {stats.rejection_rate:.1f}%\n"
                  f"**Citizens Granted:** {stats.approved_applications}\n"
                  f"**Success Score:** {'🌟' * min(5, int(stats.approval_rate / 20))}",
            inline=True
        )
        
        # Add visual progress bar for approval rate
        approval_bars = int(stats.approval_rate / 10)
        approval_visual = "█" * approval_bars + "░" * (10 - approval_bars)
        embed.add_field(
            name="📊 Approval Rate Visualization",
            value=f"`{approval_visual}` {stats.approval_rate:.1f}%",
            inline=False
        )
        
        embed.set_footer(
            text="Government of the British Virgin Islands | Statistics updated in real-time",
            icon_url="https://i.imgur.com/xqmqk9x.png"
        )
        embed.set_thumbnail(url="https://i.imgur.com/xqmqk9x.png")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdminManagementCommands:
    """Advanced admin commands for comprehensive management"""
    
    def __init__(self, bot, application_tracker: ApplicationTracker):
        self.bot = bot
        self.application_tracker = application_tracker
    
    async def bulk_operations_command(self, interaction: discord.Interaction, operation: str, user_list: str):
        """Bulk operations for multiple users"""
        # Check admin permissions
        if not hasattr(interaction.user, 'roles'):
            await interaction.response.send_message(
                "❌ This command can only be used in servers.",
                ephemeral=True
            )
            return
        
        user_role_ids = [role.id for role in interaction.user.roles]
        if not settings.has_admin_permission(user_role_ids):
            await interaction.response.send_message(
                settings.messages.no_permission,
                ephemeral=True
            )
            return
        
        # Process bulk operation
        users = [u.strip() for u in user_list.split(',') if u.strip()]
        results = []
        
        for user_mention in users:
            try:
                # Extract user ID from mention
                user_id = int(user_mention.strip('<@!>'))
                user = interaction.guild.get_member(user_id)
                
                if not user:
                    results.append(f"❌ {user_mention}: User not found")
                    continue
                
                if operation == "approve":
                    # Approve citizenship
                    if hasattr(self.bot, 'pending_applications') and user_id in self.bot.pending_applications:
                        application = self.bot.pending_applications[user_id]
                        application.status = ApplicationStatus.APPROVED
                        self.application_tracker.record_citizenship_granted(user_id, str(user))
                        results.append(f"✅ {user.mention}: Approved")
                    else:
                        results.append(f"⚠️ {user.mention}: No pending application")
                
                elif operation == "reject":
                    # Reject citizenship
                    if hasattr(self.bot, 'pending_applications') and user_id in self.bot.pending_applications:
                        application = self.bot.pending_applications[user_id]
                        application.status = ApplicationStatus.REJECTED
                        results.append(f"❌ {user.mention}: Rejected")
                    else:
                        results.append(f"⚠️ {user.mention}: No pending application")
                
            except ValueError:
                results.append(f"❌ {user_mention}: Invalid user format")
            except Exception as e:
                results.append(f"❌ {user_mention}: Error - {str(e)}")
        
        # Create results embed
        embed = discord.Embed(
            title=f"📋 Bulk {operation.title()} Results",
            color=0x3498db,
            description=f"Processed {len(users)} users:",
            timestamp=discord.utils.utcnow()
        )
        
        # Split results into chunks to avoid embed limit
        result_text = "\n".join(results)
        if len(result_text) > 4000:
            result_text = result_text[:4000] + "\n... (truncated)"
        
        embed.add_field(
            name="Results",
            value=result_text,
            inline=False
        )
        
        embed.set_footer(
            text=f"Bulk operation performed by {interaction.user}",
            icon_url="https://i.imgur.com/xqmqk9x.png"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def advanced_statistics_command(self, interaction: discord.Interaction, time_period: str = "all"):
        """Advanced statistics with filtering options"""
        # Check admin permissions
        if not hasattr(interaction.user, 'roles'):
            await interaction.response.send_message(
                "❌ This command can only be used in servers.",
                ephemeral=True
            )
            return
        
        user_role_ids = [role.id for role in interaction.user.roles]
        if not settings.has_citizenship_permission(user_role_ids):
            await interaction.response.send_message(
                settings.messages.no_citizenship_permission,
                ephemeral=True
            )
            return
        
        stats = self.application_tracker.get_statistics()
        
        embed = discord.Embed(
            title="📊 Advanced Citizenship Analytics",
            color=0x2c3e50,
            description=f"**Comprehensive statistics for: {time_period.title()}**",
            timestamp=discord.utils.utcnow()
        )
        
        # Overview section
        embed.add_field(
            name="📈 Application Overview",
            value=f"```\nTotal Applications: {stats.total_applications}\n"
                  f"Pending Review:     {stats.pending_applications}\n"
                  f"Approved:           {stats.approved_applications}\n"
                  f"Rejected:           {stats.rejected_applications}\n"
                  f"Success Rate:       {stats.approval_rate:.1f}%```",
            inline=False
        )
        
        # Time-based analytics
        embed.add_field(
            name="📅 Time-Based Analytics",
            value=f"```\nDaily Applications:   {stats.daily_applications}\n"
                  f"Weekly Applications:  {stats.weekly_applications}\n"
                  f"Monthly Applications: {stats.monthly_applications}\n"
                  f"Avg Processing Time:  {stats.average_processing_time} days```",
            inline=False
        )
        
        # User engagement metrics
        total_users = len(self.application_tracker.user_activities)
        active_users = sum(1 for activity in self.application_tracker.user_activities.values() 
                          if activity.last_application and 
                          (datetime.now() - activity.last_application).days <= 7)
        
        embed.add_field(
            name="👥 User Engagement",
            value=f"```\nTotal Registered Users: {total_users}\n"
                  f"Active This Week:       {active_users}\n"
                  f"Citizens Granted:       {stats.approved_applications}\n"
                  f"Repeat Applications:    {sum(1 for a in self.application_tracker.user_activities.values() if a.application_count > 1)}```",
            inline=False
        )
        
        # Visual chart (simple text-based)
        if stats.total_applications > 0:
            approved_width = int((stats.approved_applications / stats.total_applications) * 20)
            rejected_width = int((stats.rejected_applications / stats.total_applications) * 20)
            pending_width = 20 - approved_width - rejected_width
            
            chart = (
                f"```\n"
                f"Approved: {'█' * approved_width}{'░' * (20 - approved_width)} {stats.approved_applications}\n"
                f"Rejected: {'█' * rejected_width}{'░' * (20 - rejected_width)} {stats.rejected_applications}\n"
                f"Pending:  {'█' * pending_width}{'░' * (20 - pending_width)} {stats.pending_applications}\n"
                f"```"
            )
            embed.add_field(
                name="📊 Application Distribution",
                value=chart,
                inline=False
            )
        
        embed.set_footer(
            text=f"Analytics generated by {interaction.user} | British Virgin Islands Government",
            icon_url="https://i.imgur.com/xqmqk9x.png"
        )
        embed.set_thumbnail(url="https://i.imgur.com/xqmqk9x.png")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Global application tracker instance
application_tracker = ApplicationTracker()