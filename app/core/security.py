from bcrypt import checkpw, gensalt, hashpw


class Hasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except ValueError:
            return False
