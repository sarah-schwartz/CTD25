class Command:
    def __init__(self, piece_id: str, type: str, params: dict, timestamp_ms: int):
        self.piece_id = piece_id
        self.type = type
        self.params = params
        self.timestamp_ms = timestamp_ms

    def __str__(self):
        return (
            f"[COMMAND] {self.type.upper()} "
            f"| piece: {self.piece_id} "
            f"| from: {self.params.get('from')} -> to: {self.params.get('target')}"
        )
