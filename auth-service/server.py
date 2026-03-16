"""Authentication Service"""
import datetime
import os
from typing import Any, Optional, Protocol, Tuple, cast
import jwt
from flask import Flask, request
from pydantic import BaseModel, Field

from flask_mysqldb import MySQL  # pyright: ignore[reportMissingTypeStubs]


class CursorProtocol(Protocol):
    """Minimal cursor protocol used by this service."""

    def execute(self, query: str, args: tuple[str]) -> int: ...

    def fetchone(self) -> Optional[Tuple[str, str]]: ...


class ConnectionProtocol(Protocol):
    """Minimal DB connection protocol used by this service."""

    def cursor(self) -> CursorProtocol: ...


jwt_any: Any = jwt

class User(BaseModel):
    """User model for authentication."""
    email: str = Field(max_length=255, description="The email of the user")
    password: str = Field(max_length=255, description="The password of the user")


server = Flask(__name__)
mysql = MySQL(server)

server.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
server.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'myuser')
server.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'mypassword')
server.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'mydb')
server.config['PORT'] = os.getenv('PORT', "3306")


def create_jwt(username: str, secret: str, authz: bool) -> str:
    """Create a JWT token for the given username and secret."""
    return cast(
        str,
        jwt_any.encode(
            {
                "username": username,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=1),
                "iat": datetime.datetime.now(datetime.timezone.utc),
                "admin": authz,
            },
            secret,
            algorithm="HS256",
        ),
    )


@server.route("/login", methods=["POST"])
def login():
    """Login to the application."""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return "Missing credentials", 401

    mysql_any: Any = mysql
    conn = cast(ConnectionProtocol, mysql_any.connection)
    cur = conn.cursor()
    row_count: int = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if row_count > 0:
        user_row = cur.fetchone()
        if not user_row:
            return "Invalid credentials", 401

        email, password = user_row

        if auth.username != email or auth.password != password:
            return "Invalid credentials", 401

        return create_jwt(auth.username, os.getenv('JWT_SECRET', 'mysecret'), True)

    return "Invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    """Validate a JWT token."""
    encoded_jwt = request.headers.get("Authorization", "")
    if not encoded_jwt:
        return "Missing token", 401
    if not encoded_jwt.startswith("Bearer "):
        return "Invalid token", 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded_jwt = cast(
            dict[str, Any],
            jwt_any.decode(
                encoded_jwt,
                os.getenv('JWT_SECRET', 'mysecret'),
                algorithms=["HS256"],
            ),
        )
        return decoded_jwt, 200
    except jwt_any.ExpiredSignatureError:
        return "Token expired", 401
    except jwt_any.InvalidTokenError:
        return "Invalid token", 401
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)