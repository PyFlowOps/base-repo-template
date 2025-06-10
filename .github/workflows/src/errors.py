"""This is the custom error module for consistent and pertinent messaging.

# Author: @philipdelorenzo-manscaped<phil.delorenzo@manscaped.com>
"""

# Example
"""
class generatePackageJsonMissingError(Exception):
    def __init__(self, app: str):
        self.app = app
        # Call the base class constructor with the parameters it needs
        self.message = f"[ERROR] - {self.app} generatePackageJson key is missing, or is not set to true in project.json"
        print(self.message)
        exit(1)
"""
pass
