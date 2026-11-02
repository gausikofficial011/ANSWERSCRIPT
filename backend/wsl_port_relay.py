"""
backend/wsl_port_relay.py — Bridges WSL Postgres and Redis to Windows localhost
Listens on 0.0.0.0:5432 -> forwards to 127.0.0.1:5433 (Postgres)
Listens on 0.0.0.0:6379 -> forwards to 127.0.0.1:6380 (Redis)
"""

import asyncio
import sys

async def forward(source_reader, source_writer, target_port):
    try:
        target_reader, target_writer = await asyncio.open_connection('127.0.0.1', target_port)
    except Exception as e:
        source_writer.close()
        return

    async def pipe(r, w):
        try:
            while True:
                data = await r.read(65536)
                if not data:
                    break
                w.write(data)
                await w.drain()
        except Exception:
            pass
        finally:
            try:
                w.close()
            except Exception:
                pass

    await asyncio.gather(
        pipe(source_reader, target_writer),
        pipe(target_reader, source_writer),
        return_exceptions=True
    )

async def main():
    pg_server = await asyncio.start_server(
        lambda r, w: forward(r, w, 5433),
        '0.0.0.0', 5432, reuse_port=True
    )
    redis_server = await asyncio.start_server(
        lambda r, w: forward(r, w, 6380),
        '0.0.0.0', 6379, reuse_port=True
    )
    print("RELAY_READY: 5432->5433, 6379->6380", flush=True)
    async with pg_server, redis_server:
        await asyncio.gather(
            pg_server.serve_forever(),
            redis_server.serve_forever()
        )

if __name__ == '__main__':
    asyncio.run(main())
