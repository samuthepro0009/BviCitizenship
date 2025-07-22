from enum import Enum
from dataclasses import dataclass
from typing import Optional
import discord

class ApplicationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class CitizenshipApplication:
    user_id: int
    user_name: str
    roblox_username: str
    discord_username: str
    reason: str
    criminal_record: str
    additional_info: str
    status: ApplicationStatus = ApplicationStatus.PENDING
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        # Ensure strings are properly trimmed
        self.roblox_username = self.roblox_username.strip()
        self.discord_username = self.discord_username.strip()
        self.reason = self.reason.strip()
        self.criminal_record = self.criminal_record.strip()
        self.additional_info = self.additional_info.strip() if self.additional_info else ""
