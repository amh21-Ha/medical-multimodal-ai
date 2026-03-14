from __future__ import annotations

from dataclasses import dataclass

try:
    import jwt
except Exception:  # pragma: no cover
    jwt = None
from fastapi import Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.config import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user_id: str
    roles: list[str]
    auth_type: str


def _decode_jwt(token: str) -> AuthContext:
    if jwt is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT support unavailable")

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token") from exc

    roles = payload.get("roles", [])
    if not isinstance(roles, list):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token roles")
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    return AuthContext(user_id=user_id, roles=[str(role) for role in roles], auth_type="jwt")


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
    x_api_key: str | None = Header(default=None),
) -> AuthContext:
    settings = get_settings()
    if credentials and credentials.scheme.lower() == "bearer":
        return _decode_jwt(credentials.credentials)

    if settings.allow_api_key_fallback:
        expected = settings.api_key
        if x_api_key and x_api_key == expected:
            return AuthContext(user_id="api-key-user", roles=["admin"], auth_type="api_key")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


def require_roles(required_roles: list[str]):
    async def _dependency(context: AuthContext = Security(require_auth)) -> AuthContext:
        role_set = {role.lower() for role in context.roles}
        if not any(role.lower() in role_set for role in required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return context

    return _dependency


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Backward-compatible helper for services still using key-based auth.
    expected = get_settings().api_key
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
