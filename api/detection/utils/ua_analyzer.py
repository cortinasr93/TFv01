from typing import Dict
import ua_parser.user_agent_parser
from .constants import BOT_INDICATORS, MOBILE_OS

class UserAgentAnalyzer:
    """
    Analyzes User Agent strings to extract detailed information about the client.
    """
    
    def analyze_user_agent(self, user_agent_string: str) -> Dict:
        """
        Parse and analyze a user agent string to extract detailed information.
        
        Args:
            user_agent_string: The raw user agent string from the request
            
        Returns:
            Dict containing parsed user agent information
        """
        # Parse the user agent string
        parsed_ua = ua_parser.user_agent_parser.Parse(user_agent_string)
        
        # Extract user agent details
        user_agent = parsed_ua['user_agent']
        browser = {
            'family': user_agent['family'],
            'major': user_agent['major'],
            'minor': user_agent['minor'],
            'patch': user_agent['patch']
        }
        
        # Extract operating system details
        os = parsed_ua['os']
        operating_system = {
            'family': os['family'],
            'major': os['major'],
            'minor': os['minor'],
            'patch': os['patch'],
            'patch_minor': os['patch_minor']
        }
        
        # Extract device details
        device = parsed_ua['device']
        device_info = {
            'family': device['family'],
            'brand': device['brand'],
            'model': device['model']
        }
        
        return {
            'browser': browser,
            'operating_system': operating_system,
            'device': device_info,
            'is_mobile': self._is_mobile_device(operating_system['family']),
            'is_bot': self._check_bot_indicators(browser['family'])
        }
    
    def _is_mobile_device(self, os_family: str) -> bool:
        """Check if the operating system indicates a mobile device."""
        return os_family in MOBILE_OS
    
    def _check_bot_indicators(self, browser_family: str) -> bool:
        """Check if the browser family indicates a bot."""
        return any(indicator in browser_family for indicator in BOT_INDICATORS)