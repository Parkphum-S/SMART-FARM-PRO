from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import auth
import persistence


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, object]:
    try:
        payload = auth.decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError, auth.jwt.InvalidTokenError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    try:
        user = persistence.get_user_by_id(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable",
        ) from exc

    if user is None or not user["is_active"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    return user


def require_permission(permission: str):
    def dependency(
        user: dict[str, object] = Depends(get_current_user),
    ) -> dict[str, object]:
        try:
            permissions = persistence.get_user_permissions(int(user["id"]))
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Authorization service unavailable",
            ) from exc

        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

        return user

    return dependency


def require_farm_permission(permission: str):
    """Require a permission within the farm identified by the route path."""
    def dependency(
        farm_code: str,
        user: dict[str, object] = Depends(get_current_user),
    ) -> dict[str, object]:
        try:
            permissions = persistence.get_farm_user_permissions(
                user_id=int(user["id"]),
                farm_code=farm_code,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Farm authorization service unavailable",
            ) from exc

        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

        return user

    return dependency
