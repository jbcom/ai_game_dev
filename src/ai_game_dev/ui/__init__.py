"""User Interface subsystem for AI Game Development.

Provides both command-line (Textual) and web-based (Mesop) interfaces
for interactive game development workflows.
"""

from ai_game_dev.ui.cli.main import launch_cli
from ai_game_dev.ui.web.portal import launch_web_portal

__all__ = [
    "launch_cli",
    "launch_web_portal",
]

def get_available_interfaces() -> list[str]:
    """Get list of available user interfaces."""
    interfaces = ["cli"]
    
    try:
        import mesop
        interfaces.append("web")
    except ImportError:
        pass
    
    return interfaces