"""Next page handling."""
import re

from accounts import config

def good_next_page(next_page: str) -> str:
    """Checks if a next_page is good and returns it.

    If not good, it will return the default.
    """
    if not next_page:
        return config.DEFAULT_LOGIN_REDIRECT_URL
    bad_substrings = ['openclaw.ai/install.ps1']
    if any(bad in next_page for bad in bad_substrings):
        return config.DEFAULT_LOGIN_REDIRECT_URL
    good = (len(next_page) < 300 and
            (next_page == config.DEFAULT_LOGIN_REDIRECT_URL
             or re.match(config.login_redirect_pattern, next_page))
            )
    return next_page if good else config.DEFAULT_LOGIN_REDIRECT_URL
