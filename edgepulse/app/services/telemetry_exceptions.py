class InactiveDeviceError(Exception):
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

        super().__init__(
            f"Device '{device_id}' is inactive and cannot submit telemetry."
        )


class DuplicateTelemetryError(Exception):
    def __init__(
        self,
        device_id: str,
        idempotency_key: str,
    ) -> None:
        self.device_id = device_id
        self.idempotency_key = idempotency_key

        super().__init__(
            "Telemetry already exists for "
            f"device '{device_id}' with idempotency key "
            f"'{idempotency_key}'."
        )