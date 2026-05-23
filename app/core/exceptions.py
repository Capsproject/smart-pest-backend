from fastapi import HTTPException, status


def not_found(entity: str = "Resource") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")


def already_exists(entity: str = "Resource") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{entity} already exists")


def credentials_invalid() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(detail: str = "Not enough privileges") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
