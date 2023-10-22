__all__: list[str] = [
    "CLIUtils",
]


class CLIUtils:
    @classmethod
    def get_readable_duration(cls, time_per_it: float, total_it: int) -> str:
        hours, remainder = divmod(time_per_it * total_it, 3_600)
        minutes, seconds = divmod(remainder, 60)
        time_seq: list[float] = [t for t in (hours, minutes, seconds) if t]
        return ":".join(map(lambda t: f"{int(t):02}", time_seq))
