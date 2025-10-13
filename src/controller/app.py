from atomic import Atomic

from src.infrastructure.config import prefix
from src.infrastructure.config.business_action import (
    BusinessActionDefinitionCustom
)

app = Atomic(__name__, prefix=prefix)
app_2 = app.create_app()
app_2.config.update(
    {"business_action_provider": [BusinessActionDefinitionCustom()]}
)
