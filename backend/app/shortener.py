ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)
MIN_LEN = 4


def encode(n: int) -> str:
    if n < 0:
        raise ValueError("negative id")

    out = []

    while n > 0:
        n, rem = divmod(n, BASE)
        out.append(ALPHABET[rem])

    code = "".join(reversed(out)) or "0"

    return code.rjust(MIN_LEN, ALPHABET[0])