import random
import time
import json
import os
import logging

class TimingUtils:
    def __init__(self, config_path='config/settings.json'):
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join(os.path.dirname(__file__), f'../{config_path}')
        self.delays = self.load_delays()

    def load_delays(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get('delays', {'min_wait': 2, 'max_wait': 5})
        except Exception as e:
            self.logger.error(f"Error loading delays: {str(e)}")
            return {'min_wait': 2, 'max_wait': 5}

    def random_delay(self, min_wait=None, max_wait=None):
        """Apply a random delay between min_wait and max_wait seconds."""
        min_delay = min_wait if min_wait is not None else self.delays['min_wait']
        max_delay = max_wait if max_wait is not None else self.delays['max_wait']
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"Applying random delay of {delay:.2f} seconds")
        time.sleep(delay)