from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, entity: str, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{entity} com ID {identifier} não encontrado'
        )

class ConflictError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class BadRequestError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
