import jwt
import datetime
import os


def create_tiny_token() -> str:
    exp = int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600
    payload = {
        "x": exp
    }

    token = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm="HS256")
    return token


def verify_token_expiration(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,  os.environ['SECRET_KEY'], algorithms=["HS256"])

        exp_timestamp = decoded.get("x")
        if not exp_timestamp:
            return {"error": "No expiration date in token"}

        exp_datetime = datetime.datetime.fromtimestamp(
            exp_timestamp, tz=datetime.timezone.utc)
        current_datetime = datetime.datetime.now(datetime.timezone.utc)

        if current_datetime > exp_datetime:
            return True

        return False

    except jwt.InvalidTokenError:
        return True
    except jwt.DecodeError:
        return True
