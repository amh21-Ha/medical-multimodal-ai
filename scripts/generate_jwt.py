#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import jwt


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate JWT for local testing")
    parser.add_argument("--secret", required=True)
    parser.add_argument("--subject", default="local-user")
    parser.add_argument("--roles", default="analyst", help="Comma-separated roles")
    parser.add_argument("--issuer", default="multimodal-medical-ai")
    parser.add_argument("--audience", default="multimodal-medical-ai-users")
    parser.add_argument("--expires-min", type=int, default=60)
    parser.add_argument("--algorithm", default="HS256")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": args.subject,
        "roles": [role.strip() for role in args.roles.split(",") if role.strip()],
        "iss": args.issuer,
        "aud": args.audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=args.expires_min)).timestamp()),
    }

    token = jwt.encode(payload, args.secret, algorithm=args.algorithm)
    print(token)


if __name__ == "__main__":
    main()
