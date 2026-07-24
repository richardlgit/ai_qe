class DeviceAlreadyExistsError(Exception):
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

        super().__init__(
            f"Device '{device_id}' already exists."
        )


class DeviceNotFoundError(Exception):
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

        super().__init__(
            f"Device '{device_id}' was not found."
        )