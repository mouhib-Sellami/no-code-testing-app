
class EngineMissingArgs(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EngineMissingTaskTypes(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EngineMissingWorkerClass(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskMissingWorkerClass(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
