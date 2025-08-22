#!/bin/bash

# Script to switch between Claude settings configurations
# Usage: ./scripts/switch-claude.sh [ant|aws|status|-h|--help]

CLAUDE_DIR=".claude"
LOCAL_SETTINGS="$CLAUDE_DIR/settings.local.json"
ANT_SETTINGS="$CLAUDE_DIR/settings.local.ant.json"
AWS_SETTINGS="$CLAUDE_DIR/settings.local.aws.json"

# Function to display help/manual
show_help() {
    cat << HELP
switch-claude.sh - Claude Settings Switcher

DESCRIPTION:
    This script switches between different Claude settings configurations by
    creating symlinks to the appropriate settings file.

USAGE:
    ./scripts/switch-claude.sh [COMMAND]

COMMANDS:
    ant         Switch to Anthropic settings (.claude/settings.local.ant.json)
    aws         Switch to AWS settings (.claude/settings.local.aws.json)
    status      Show current active settings configuration
    -h, --help  Show this help message

EXAMPLES:
    ./scripts/switch-claude.sh ant      # Switch to Anthropic settings
    ./scripts/switch-claude.sh aws      # Switch to AWS settings
    ./scripts/switch-claude.sh status   # Check current configuration
    ./scripts/switch-claude.sh -h       # Show help

NOTES:
    - The script must be run from the project root directory
    - Settings files must exist before switching (.claude/settings.local.ant.json and .claude/settings.local.aws.json)
    - The script creates a symlink at .claude/settings.local.json pointing to the selected configuration

HELP
}

# Function to show current status
show_status() {
    if [ -L "$LOCAL_SETTINGS" ]; then
        TARGET=$(readlink "$LOCAL_SETTINGS")
        echo "Current settings: symlink to $TARGET"
        if [ "$TARGET" = "settings.local.ant.json" ]; then
            echo "Active configuration: Anthropic"
        elif [ "$TARGET" = "settings.local.aws.json" ]; then
            echo "Active configuration: AWS"
        else
            echo "Active configuration: Unknown ($TARGET)"
        fi
    elif [ -f "$LOCAL_SETTINGS" ]; then
        echo "Current settings: regular file (not managed by this script)"
        echo "Active configuration: Manual/Custom"
    else
        echo "No settings file found"
        echo "Active configuration: None"
    fi
}

# Check if we're in the right directory
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Error: .claude directory not found. Run this script from the project root."
    exit 1
fi

# Handle command
case "$1" in
    "ant")
        if [ ! -f "$ANT_SETTINGS" ]; then
            echo "Error: $ANT_SETTINGS not found"
            echo "Create this file before switching to Anthropic settings"
            exit 1
        fi
        
        rm -f "$LOCAL_SETTINGS"
        ln -s "settings.local.ant.json" "$LOCAL_SETTINGS"
        echo "✓ Switched to Anthropic settings"
        ;;
        
    "aws")
        if [ ! -f "$AWS_SETTINGS" ]; then
            echo "Error: $AWS_SETTINGS not found"
            echo "Create this file before switching to AWS settings"
            exit 1
        fi
        
        rm -f "$LOCAL_SETTINGS"
        ln -s "settings.local.aws.json" "$LOCAL_SETTINGS"
        echo "✓ Switched to AWS settings"
        ;;
        
    "status")
        show_status
        ;;
        
    "-h"|"--help")
        show_help
        ;;
        
    "")
        echo "Error: No command specified"
        echo "Run './scripts/switch-claude.sh -h' for help"
        exit 1
        ;;
        
    *)
        echo "Error: Unknown command '$1'"
        echo "Run './scripts/switch-claude.sh -h' for help"
        exit 1
        ;;
esac
