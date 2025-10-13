"""Local shim for proprietary 'audit' library used for business action mapping."""

class BvBusinessActionInterface:
    """Minimal interface expected by BusinessActionDefinitionCustom in tests."""

    def get_business_action(self, service: str) -> str:  # pragma: no cover - interface only
        raise NotImplementedError
