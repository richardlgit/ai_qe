class AlertNotFoundError(Exception):
    def __init__(self, alert_id: str) -> None:
        self.alert_id = alert_id

        super().__init__(
            f"Alert '{alert_id}' was not found."
        )