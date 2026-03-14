import contextvars
import uuid


request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def ensure_request_id() -> str:
    current = request_id_ctx.get()
    if current:
        return current
    new_id = str(uuid.uuid4())
    request_id_ctx.set(new_id)
    return new_id
