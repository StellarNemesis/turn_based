class TurnBasedError(Exception):
    pass


class InvalidTargetError(TurnBasedError):
    pass


class CastingError(TurnBasedError):
    pass


class DeathError(TurnBasedError):
    pass
