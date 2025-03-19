from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, detail: str):
        """Initialize the exception with a detail message."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class UnauthorizedException(HTTPException):
    """Exception raised when a user is not authorized to access a resource."""
    
    def __init__(self, detail: str):
        """Initialize the exception with a detail message."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class BadRequestException(HTTPException):
    """Exception raised when a request is invalid."""
    
    def __init__(self, detail: str):
        """Initialize the exception with a detail message."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseException(Exception):
    """Exception raised when there is an error with the database."""
    
    def __init__(self, detail: str):
        """Initialize the exception with a detail message."""
        self.detail = detail
        super().__init__(self.detail)

class AIModelException(Exception):
    """Exception raised when there is an error with an AI model."""
    
    def __init__(self, detail: str, model_name: str = None):
        """Initialize the exception with a detail message and optional model name."""
        self.detail = detail
        self.model_name = model_name
        message = f"AI Model Error: {detail}"
        if model_name:
            message += f" (Model: {model_name})"
        super().__init__(message) 