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

    user = persistence.get_user_for_auth(str(user_id))

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
        permissions = persistence.get_user_permissions(int(user["id"]))

        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

        return user

    return dependency
