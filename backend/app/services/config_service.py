"""
Configuration service for managing .env file updates
"""
import os
import re
from typing import Dict, Optional
from pathlib import Path


def get_env_path() -> Path:
    """Get the path to the .env file"""
    # Get backend directory path
    backend_dir = Path(__file__).parent.parent.parent
    env_path = backend_dir / ".env"
    return env_path


def read_env_config() -> Dict[str, str]:
    """
    Read current configuration from .env file
    
    Returns:
        Dict with current configuration values
    """
    env_path = get_env_path()
    
    if not env_path.exists():
        return {}
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def update_env_config(updates: Dict[str, str]) -> bool:
    """
    Update specific keys in the .env file
    
    Args:
        updates: Dict of key-value pairs to update
    
    Returns:
        True if successful, False otherwise
    """
    try:
        env_path = get_env_path()
        
        if not env_path.exists():
            # Create new .env file
            with open(env_path, 'w') as f:
                for key, value in updates.items():
                    f.write(f"{key}={value}\n")
            return True
        
        # Read current content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update lines
        updated_keys = set()
        new_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Keep comments and empty lines
            if not stripped or stripped.startswith('#'):
                new_lines.append(line)
                continue
            
            # Check if this line has a key we want to update
            if '=' in stripped:
                key = stripped.split('=', 1)[0].strip()
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Add any new keys that weren't in the file
        for key, value in updates.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        # Reload environment variables
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        
        return True
        
    except Exception as e:
        print(f"Error updating .env file: {e}")
        return False


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a single configuration value"""
    config = read_env_config()
    return config.get(key, default)


def validate_config_update(updates: Dict[str, str]) -> tuple[bool, Optional[str]]:
    """
    Validate configuration updates before applying
    
    Returns:
        (is_valid, error_message)
    """
    # Validate MAX_QUESTIONS
    if "MAX_QUESTIONS" in updates:
        try:
            max_q = int(updates["MAX_QUESTIONS"])
            if max_q < 1 or max_q > 50:
                return False, "MAX_QUESTIONS must be between 1 and 50"
        except ValueError:
            return False, "MAX_QUESTIONS must be a valid integer"
    
    # Validate QUESTION_TIMEOUT_SECONDS
    if "QUESTION_TIMEOUT_SECONDS" in updates:
        try:
            timeout = int(updates["QUESTION_TIMEOUT_SECONDS"])
            if timeout < 30 or timeout > 600:
                return False, "QUESTION_TIMEOUT_SECONDS must be between 30 and 600"
        except ValueError:
            return False, "QUESTION_TIMEOUT_SECONDS must be a valid integer"
    
    return True, None
