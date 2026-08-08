class MissingDeviceTokenError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "A device bearer token is required."
        )


class InvalidDeviceTokenError(Exception):
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

        super().__init__(
            f"Invalid token for device '{device_id}'."
        )