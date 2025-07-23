# British Virgin Islands Discord Bot

## Overview

This repository contains a Discord bot designed for managing BVI (British Virgin Islands) citizenship applications. The bot provides an interactive form-based system for users to submit citizenship applications and for administrators to review and process them. The application uses Discord's modern slash commands and modal interfaces for a seamless user experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The system follows a modular, event-driven architecture built around Discord.py's command framework:

- **Bot Core**: Discord.py-based bot with slash commands and modal interactions
- **Keep-Alive Service**: Flask-based HTTP server for deployment health monitoring
- **Data Models**: Simple dataclass-based models for application management
- **Threading Architecture**: Separate threads for Discord bot and keep-alive service

## Key Components

### Discord Bot (`bot.py`)
- **CitizenshipModal**: Interactive form for collecting application data
- **Slash Commands**: Modern Discord command interface
- **Application Processing**: Handles form submissions and dual-role admin reviews
- **Role Management**: Automatic role assignment upon approval
- **Dual Permission System**: Separate Admin and Citizenship Manager roles for granular access control

### Data Models (`models.py`)
- **CitizenshipApplication**: Dataclass containing all application fields
- **ApplicationStatus**: Enum for tracking application states (pending, approved, rejected)
- **Data Validation**: Basic string trimming and validation

### Keep-Alive Service (`keep_alive.py`)
- **Flask Server**: Lightweight HTTP server for health checks
- **Self-Ping Mechanism**: Periodic health checks to prevent service sleeping
- **Monitoring Endpoints**: Health status endpoints for external monitoring

### Main Entry Point (`main.py`)
- **Threading Coordination**: Manages both Discord bot and keep-alive service
- **Service Orchestration**: Ensures both services start properly

## Data Flow

1. **Application Submission**: User triggers slash command → Modal form appears → Data collected and validated
2. **Application Storage**: Form data converted to CitizenshipApplication dataclass → Stored in memory
3. **Admin Review**: Admins can view, approve, or reject applications via Discord commands
4. **Status Updates**: Users receive notifications of application status changes
5. **Role Assignment**: Approved users automatically receive citizen role

## External Dependencies

### Discord Integration
- **discord.py**: Primary Discord API wrapper
- **Slash Commands**: Modern Discord command system
- **Modals & UI**: Interactive form components

### Keep-Alive Infrastructure
- **Flask**: Lightweight web framework for health endpoints
- **Requests**: HTTP client for self-ping functionality
- **Threading**: Concurrent execution of services

### Environment Dependencies
- **Discord Bot Token**: Required for Discord API authentication
- **PORT**: Configurable port for Flask server (defaults to 5000)
- **RENDER_EXTERNAL_URL**: External URL for self-ping functionality
- **ADMIN_ROLE_ID**: Optional role ID for full admin permissions (ban users, manage citizenship)
- **CITIZENSHIP_MANAGER_ROLE_ID**: Optional role ID for citizenship management only (cannot ban users)

## Deployment Strategy

The application is designed for cloud deployment with the following characteristics:

### Service Management
- **Multi-threaded Architecture**: Discord bot and Flask server run concurrently
- **Health Monitoring**: Built-in health check endpoints
- **Auto-restart**: Self-ping mechanism prevents service hibernation

### Environment Configuration
- **Environment Variables**: All sensitive configuration via environment variables
- **Port Flexibility**: Configurable port binding for different deployment platforms
- **Logging**: Structured logging for monitoring and debugging

### Data Persistence
- **In-Memory Storage**: Current implementation uses runtime memory
- **Stateless Design**: Application data not persisted between restarts
- **Future Enhancement**: Ready for database integration (likely PostgreSQL with Drizzle ORM)

### Scalability Considerations
- **Single Instance**: Current design for single bot instance
- **Role-Based Access**: Dual-tier permission system with Admin and Citizenship Manager roles
- **Granular Permissions**: Citizenship managers can approve/decline but cannot ban users
- **Rate Limiting**: Discord API rate limiting handled by discord.py

## Key Architectural Decisions

### Modal-Based Forms
- **Problem**: Need user-friendly application submission
- **Solution**: Discord modals with multiple input fields
- **Rationale**: Provides better UX than multi-step command interactions

### In-Memory Storage
- **Problem**: Need to store application data
- **Solution**: Runtime memory with dataclasses
- **Trade-off**: Simple implementation but data loss on restart

### Keep-Alive Pattern
- **Problem**: Cloud services may hibernate inactive applications
- **Solution**: Self-pinging Flask server
- **Rationale**: Ensures consistent bot availability without external monitoring

### Threaded Architecture
- **Problem**: Need both Discord bot and web server
- **Solution**: Separate threads for each service
- **Rationale**: Allows independent operation while sharing resources

### Dual Permission System
- **Problem**: Need flexible access control for different admin levels
- **Solution**: Separate Admin and Citizenship Manager roles with different capabilities
- **Rationale**: Allows delegation of citizenship management without full admin privileges

## Recent Changes

### July 23, 2025 - Comprehensive Feature Enhancement & Custom BVI Images
- **Image Upload**: Successfully uploaded custom BVI coat of arms images to imgur
  - Icon (coat of arms): https://i.imgur.com/xqmqk9x.png
  - Banner (British Virgin Islands): https://i.imgur.com/Pf2iXAV.png (updated with new design)
- **Advanced Features Module**: Created comprehensive advanced_features.py with:
  - ApplicationTracker for detailed analytics and user activity monitoring
  - Enhanced statistics with approval rates, processing times, and engagement metrics
  - EnhancedCitizenshipDashboard with 5 interactive buttons and detailed status tracking
  - Real-time application statistics and visual progress bars
- **Notification System**: Implemented notification_system.py with:
  - Comprehensive notification templates for all application states
  - Automated DM system with professional branding
  - Bulk notification capabilities for administrators
  - Scheduled notification system for follow-ups
  - Welcome message automation for new members
- **Enhanced Admin Commands**: Created enhanced_admin_commands.py featuring:
  - Advanced statistics dashboard with performance metrics
  - Bulk approval system for multiple applications
  - Server-wide announcement system with role pinging
  - Maintenance notice automation with scheduling
  - Comprehensive administrative tools and reporting
- **User Experience Improvements**: 
  - Interactive dashboard with application guide, support center, and statistics
  - Enhanced status checking with detailed information and timelines
  - Professional embedded interfaces with consistent BVI branding
  - Real-time activity tracking and engagement monitoring
- **Architectural Enhancements**:
  - Modular design with separated concerns for scalability
  - Advanced error handling and logging throughout all modules
  - Comprehensive data models for tracking user activities and statistics
  - Professional-grade administrative interfaces and tools

### July 22, 2025 - Replit Migration & Console Output Optimization
- **Replit Migration**: Successfully migrated from Replit Agent to standard Replit environment
- **Interactive Citizenship Dashboard**: Complete redesign of citizenship command interface
  - Added beautiful BVI banner image integration (https://i.imgur.com/G1wrrwI.png)
  - Created interactive button-based dashboard with 4 main functions:
    - Apply for Citizenship (primary action button)
    - Check Application Status (real-time status checking)
    - Citizenship Information (benefits and requirements)
    - Contact Support (help and troubleshooting)
  - Implemented proper timeout handling and button management
- **Enhanced Configuration System**: Reorganized both role and channel management
  - **Role Configuration**: Clean sections for ADMIN_ROLES and CITIZENSHIP_MANAGER_ROLES
  - **Channel Configuration**: Added support for both channel IDs and names
    - CHANNEL_IDS for reliable channel targeting
    - CHANNEL_NAMES as fallback method
    - Updated ChannelManager with get_channel_by_id_or_name method
- **Improved User Experience**: 
  - Professional embedded interfaces with consistent branding
  - Ephemeral responses for privacy
  - Clear status messages and error handling
  - Real-time application status tracking
- **Environment Setup**: Configured Discord bot token and session secrets
- **Workflow Configuration**: Set up proper Replit workflows for bot execution
- **Console Output Optimization**: 
  - Removed excessive logging from Discord.py, werkzeug, and other libraries
  - Added clean status messages with emojis for better readability
  - Suppressed unnecessary HTTP request logs and rate limiting warnings
  - Enhanced error reporting with clearer formatting
- **Debug Improvements**: Added comprehensive error handling and status reporting
- **Legacy Support**: Maintained backward compatibility with environment variables