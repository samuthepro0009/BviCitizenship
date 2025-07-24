"""
Image configuration for the BVI Discord Bot
Centralized management of all image URLs
"""

# New BVI Department of Immigration images - Uploaded to imgur
DEPARTMENT_ICON_URL = "https://i.imgur.com/UOoJ0NK.png"
DEPARTMENT_BANNER_URL = "https://i.imgur.com/424B8Hu.png"

# Legacy URLs (backup)
LEGACY_ICON_URL = "https://i.imgur.com/xqmqk9x.png"
LEGACY_BANNER_URL = "https://i.imgur.com/Pf2iXAV.png"

# Image configuration mapping
IMAGES = {
    'icon': DEPARTMENT_ICON_URL,
    'banner': DEPARTMENT_BANNER_URL,
    'footer_icon': DEPARTMENT_ICON_URL,
    'thumbnail': DEPARTMENT_ICON_URL,
}

def get_image_url(image_type: str) -> str:
    """Get image URL by type with fallback to legacy"""
    return IMAGES.get(image_type, LEGACY_ICON_URL)