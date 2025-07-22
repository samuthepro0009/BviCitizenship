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
- **Application Processing**: Handles form submissions and admin reviews
- **Role Management**: Automatic role assignment upon approval

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
- **Role-Based Access**: Built-in admin role checking for application management
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