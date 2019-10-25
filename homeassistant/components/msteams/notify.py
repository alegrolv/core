"""Microsoft Teams platform for notify component."""
import logging

import pymsteams
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_URL
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ATTR_FILE_URL = "image_url"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_URL): cv.url})


def get_service(hass, config, discovery_info=None):
    """Get the Microsoft Teams notification service."""
    webhook_url = config.get(CONF_URL)

    try:
        return MSTeamsNotificationService(webhook_url)

    except RuntimeError as err:
        _LOGGER.exception("Error in creating a new Microsoft Teams message: %s", err)
        return None


class MSTeamsNotificationService(BaseNotificationService):
    """Implement the notification service for Microsoft Teams."""

    def __init__(self, webhook_url):
        """Initialize the service."""
        self._webhook_url = webhook_url
        self.teams_message = pymsteams.connectorcard(self._webhook_url)

    def send_message(self, message=None, **kwargs):
        """Send a message to the webhook."""
        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        data = kwargs.get(ATTR_DATA)

        self.teams_message.title(title)

        self.teams_message.text(message)

        if data is not None:
            file_url = data.get(ATTR_FILE_URL)

            if file_url is not None:
                if not file_url.startswith("http"):
                    _LOGGER.error("URL should start with http or https")
                    return

                message_section = pymsteams.cardsection()
                message_section.addImage(file_url)
                self.teams_message.addSection(message_section)
        try:
            self.teams_message.send()
        except RuntimeError as err:
            _LOGGER.error("Could not send notification. Error: %s", err)