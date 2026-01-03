"""
SharePoint Integration Utilities.
Updates SharePoint list with verification results using Windows authentication.
"""
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import os
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path


class SharePointClient:
    """Client for SharePoint list operations."""
    
    def __init__(self, site_url: str, list_name: str):
        """
        Initialize SharePoint client.
        
        Args:
            site_url: SharePoint site URL.
            list_name: Name of the SharePoint list.
        """
        self.site_url = site_url.rstrip('/')
        self.list_name = list_name
        self.ctx: Optional[ClientContext] = None
    
    def connect(self) -> bool:
        """
        Connect to SharePoint using Windows authentication (default credentials).
        Falls back to app credentials or user credentials from environment variables.
        
        Returns:
            True if connection successful, False otherwise.
        """
        # Try Windows authentication first (uses current user's credentials)
        try:
            self.ctx = ClientContext(self.site_url).with_credentials()
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()
            return True
        except Exception as e:
            print(f"Windows authentication failed: {e}")
        
        # Try app credentials (for service account)
        if self._connect_alternative():
            return True
        
        # If no app credentials, try user credentials from environment
        return self._connect_user_credentials()
    
    def _connect_alternative(self) -> bool:
        """
        Connect using app credentials (Client ID/Secret) from environment variables.
        This is the preferred method for automated/corporate environments.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            # Check for app credentials in environment variables
            client_id = os.getenv("SHAREPOINT_CLIENT_ID")
            client_secret = os.getenv("SHAREPOINT_CLIENT_SECRET")
            
            if client_id and client_secret:
                from office365.runtime.auth.client_credential import ClientCredential
                credentials = ClientCredential(client_id, client_secret)
                self.ctx = ClientContext(self.site_url).with_credentials(credentials)
                
                # Test connection
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error with app credentials authentication: {e}")
            return False
    
    def _connect_user_credentials(self) -> bool:
        """
        Connect using user credentials from environment variables.
        For corporate environments where user credentials are stored.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            username = os.getenv("SHAREPOINT_USERNAME")
            password = os.getenv("SHAREPOINT_PASSWORD")
            
            if username and password:
                from office365.runtime.auth.user_credential import UserCredential
                credentials = UserCredential(username, password)
                self.ctx = ClientContext(self.site_url).with_credentials(credentials)
                
                # Test connection
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()
                return True
            
            # If no credentials in environment, return False
            # User should set SHAREPOINT_CLIENT_ID and SHAREPOINT_CLIENT_SECRET
            # or SHAREPOINT_USERNAME and SHAREPOINT_PASSWORD
            return False
            
        except Exception as e:
            print(f"Error with user credentials authentication: {e}")
            return False
    
    def add_verification_result(
        self,
        serial_number: str,
        config_tag: str,
        result: str,
        result_folder_path: str,
        verification_date: Optional[datetime] = None
    ) -> bool:
        """
        Add verification result to SharePoint list.
        
        Args:
            serial_number: Pump serial number.
            config_tag: Configuration tag.
            result: PASS or FAIL.
            result_folder_path: Path to result folder (for link).
            verification_date: Date of verification (defaults to now).
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.ctx is None:
                if not self.connect():
                    return False
            
            if verification_date is None:
                verification_date = datetime.now()
            
            # Get the list
            target_list = self.ctx.web.lists.get_by_title(self.list_name)
            
            # Prepare item data
            item_data = {
                "Title": f"{serial_number} - {result}",
                "SerialNumber": serial_number,
                "ConfigTag": config_tag,
                "Result": result,
                "VerificationDate": verification_date.isoformat(),
                "ResultFolder": result_folder_path,
            }
            
            # Create item
            item = target_list.add_item(item_data)
            self.ctx.execute_query()
            
            return True
            
        except Exception as e:
            print(f"Error adding result to SharePoint: {e}")
            return False
    
    def get_sorted_results(self, serial_number: Optional[str] = None) -> list:
        """
        Get verification results sorted by time (ascending).
        Useful for detecting duplicate files.
        
        Args:
            serial_number: Optional filter by serial number.
            
        Returns:
            List of result items sorted by verification date.
        """
        try:
            if self.ctx is None:
                if not self.connect():
                    return []
            
            target_list = self.ctx.web.lists.get_by_title(self.list_name)
            items = target_list.items
            
            if serial_number:
                items = items.filter(f"SerialNumber eq '{serial_number}'")
            
            self.ctx.load(items)
            self.ctx.execute_query()
            
            # Sort by VerificationDate (ascending)
            results = []
            for item in items:
                results.append({
                    "id": item.properties.get("Id"),
                    "serial_number": item.properties.get("SerialNumber"),
                    "config_tag": item.properties.get("ConfigTag"),
                    "result": item.properties.get("Result"),
                    "date": item.properties.get("VerificationDate"),
                    "folder": item.properties.get("ResultFolder"),
                })
            
            # Sort by date (ascending)
            results.sort(key=lambda x: x.get("date", ""))
            return results
            
        except Exception as e:
            print(f"Error getting results from SharePoint: {e}")
            return []

