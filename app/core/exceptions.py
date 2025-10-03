# Purpose: Исключения для доменной логики Family Habit.
# Context: Custom exceptions with error codes for API responses and logging.
# Requirements: Clear error codes, human-readable messages, inheritance hierarchy.


class FamilyHabitError(Exception):
    """Базовое исключение для Family Habit."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DomainError(FamilyHabitError):
    """Ошибки бизнес-логики."""
    pass


class ValidationError(FamilyHabitError):
    """Ошибки валидации данных."""
    pass


class NotFoundError(FamilyHabitError):
    """Ресурс не найден."""
    pass


class PermissionError(FamilyHabitError):
    """Недостаточно прав доступа."""
    pass


class LimitError(FamilyHabitError):
    """Превышение лимитов тарифного плана."""
    pass


# Предустановленные исключения для частых случаев

class TaskNotFoundError(NotFoundError):
    """Задание не найдено."""
    
    def __init__(self, task_id: int):
        super().__init__(
            code="task_not_found",
            message=f"Задание {task_id} не найдено",
            details={"task_id": task_id}
        )


class ChildNotFoundError(NotFoundError):
    """Ребёнок не найден."""
    
    def __init__(self, child_id: int):
        super().__init__(
            code="child_not_found", 
            message=f"Ребёнок {child_id} не найден",
            details={"child_id": child_id}
        )


class ParentNotFoundError(NotFoundError):
    """Родитель не найден."""
    
    def __init__(self, parent_id: int):
        super().__init__(
            code="parent_not_found",
            message=f"Родитель {parent_id} не найден", 
            details={"parent_id": parent_id}
        )


class TaskAlreadySubmittedError(DomainError):
    """Задание уже выполнено."""
    
    def __init__(self, task_id: int):
        super().__init__(
            code="task_already_submitted",
            message=f"Задание {task_id} уже выполнено",
            details={"task_id": task_id}
        )


class InsufficientFundsError(DomainError):
    """Недостаточно средств для покупки."""
    
    def __init__(self, required: int, available: int):
        super().__init__(
            code="insufficient_funds",
            message=f"Недостаточно монет: нужно {required}, доступно {available}",
            details={"required": required, "available": available}
        )