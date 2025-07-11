import os
from typing import Optional

class AIConfig:
    
    def __init__(self):
        self.base_url: str = os.getenv('AI_BASE_URL', 'https://api.deepseek.com/v1')
        self.model: str = os.getenv('AI_MODEL', 'deepseek-chat')
        self.temperature: float = float(os.getenv('AI_TEMPERATURE', '0'))

config = AIConfig() 