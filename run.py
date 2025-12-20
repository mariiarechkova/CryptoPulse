import asyncio
import ssl

import certifi


def safe_default_context(*args, **kwargs):
    ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(certifi.where())

    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


ssl.create_default_context = safe_default_context  # type: ignore

import main  # noqa: E402

if __name__ == "__main__":
    asyncio.run(main.main())
