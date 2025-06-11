#!/usr/bin/env python3
import subprocess
import re

class CommandResult:
    def __init__(self, success, message, details=None):
        self.success = success
        self.message = message
        self.details = details or {}

def run_command(command, update_progress):
    """Execute a shell command and update progress."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    
    lines = []
    current_progress = 0.0
    
    stdout = process.stdout
    if stdout is not None:
        for output in stdout:
            if output:
                lines.append(output.strip())
                current_progress = min(current_progress + 0.01, 0.99)
                if not update_progress(current_progress, output.strip()):
                    process.terminate()
                    return CommandResult(False, "Operation cancelled")
    
    return_code = process.poll()
    stderr = process.stderr.read() if process.stderr else ""
    
    if return_code == 0:
        return CommandResult(True, "Completed", {"output": lines})
    else:
        return CommandResult(False, f"Error: {stderr}")

def parse_upgrade_output(output):
    """Parse apt/apt-fast upgrade output to count packages"""
    if not output:
        return {"upgraded": 0, "newly_installed": 0, "to_remove": 0}
    
    stats = {"upgraded": 0, "newly_installed": 0, "to_remove": 0}
    
    for line in output:
        if "upgraded," in line:
            matches = re.findall(r'(\d+) upgraded', line)
            if matches:
                stats["upgraded"] = int(matches[0])
        if "newly installed" in line:
            matches = re.findall(r'(\d+) newly installed', line)
            if matches:
                stats["newly_installed"] = int(matches[0])
        if "to remove" in line:
            matches = re.findall(r'(\d+) to remove', line)
            if matches:
                stats["to_remove"] = int(matches[0])
    
    return stats

def update_repos(update_progress):
    """Update system repositories."""
    result = run_command("pkexec apt-get update", update_progress)
    if result.success:
        return CommandResult(True, "Repositories updated successfully")
    return result

def upgrade_packages(update_progress):
    """Upgrade system packages."""
    result = run_command("pkexec apt-get upgrade -y", update_progress)
    if result.success:
        stats = parse_upgrade_output(result.details.get("output", []))
        return CommandResult(True, "Packages upgraded successfully", stats)
    return result

def update_flatpak(update_progress):
    """Update Flatpak applications."""
    result = run_command("flatpak update -y", update_progress)
    if result.success:
        updates = sum(1 for line in result.details.get("output", []) if "Installing" in line)
        return CommandResult(True, "Flatpak applications updated successfully", {"updated": updates})
    return result

def clean_packages(update_progress):
    """Clean package cache."""
    result = run_command("pkexec apt-get clean", update_progress)
    if result.success:
        return CommandResult(True, "Package cache cleaned successfully")
    return result

def autoremove_packages(update_progress):
    """Remove unused packages."""
    result = run_command("pkexec apt-get autoremove -y", update_progress)
    if result.success:
        removed = sum(1 for line in result.details.get("output", []) if "Removing" in line)
        return CommandResult(True, "Unused packages removed successfully", {"removed": removed})
    return result

def update_all(update_progress):
    """Update everything (except distribution)."""
    commands = [
        ("pkexec apt-get update", "Repository update"),
        ("pkexec apt-get upgrade -y", "Package upgrade"),
        ("flatpak update -y", "Flatpak update")
    ]
    
    total_stats = {"upgraded": 0, "newly_installed": 0, "to_remove": 0, "flatpak_updated": 0}
    
    for i, (cmd, _) in enumerate(commands):
        progress_base = i / len(commands)
        progress_step = 1.0 / len(commands)
        
        def make_progress_callback(base, step):
            def callback(p, s):
                return update_progress(base + p * step, s)
            return callback
        
        result = run_command(cmd, make_progress_callback(progress_base, progress_step))
        if not result.success:
            return result
            
        if "upgrade" in cmd:
            stats = parse_upgrade_output(result.details.get("output", []))
            total_stats.update(stats)
        elif "flatpak" in cmd:
            updates = sum(1 for line in result.details.get("output", []) if "Installing" in line)
            total_stats["flatpak_updated"] = updates
    
    return CommandResult(True, "All updates completed successfully", total_stats)

def check_system_status(update_progress):
    """Check system status."""
    commands = {
        "Disk Usage": "df -h",
        "Memory Usage": "free -h",
        "System Uptime": "uptime",
        "Updates Available": "apt list --upgradable 2>/dev/null | grep -v 'Listing...' | wc -l"
    }
    
    status = {}
    current_step = 0
    total_steps = len(commands)

    for description, cmd in commands.items():
        current_step += 1
        progress = current_step / total_steps
        update_progress(progress, f"Checking {description}...")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                universal_newlines=True
            )
            output, _ = process.communicate()
            status[description] = output.strip()
        except Exception as e:
            status[description] = f"Error: {str(e)}"

    # Format the status information
    formatted_status = (
        f"System Status Report\n"
        f"-------------------\n\n"
        f"Disk Usage:\n{status['Disk Usage']}\n\n"
        f"Memory Usage:\n{status['Memory Usage']}\n\n"
        f"System Uptime:\n{status['System Uptime']}\n\n"
        f"Updates Available: {status['Updates Available']} packages"
    )

    return CommandResult(True, "System status check completed", 
                        {"status": formatted_status})