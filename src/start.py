from lib_process import asyncio, ssl  # bỏ global_vars nếu không cần
from server_process import server_process
import hypercorn.asyncio
from hypercorn.config import Config
from api_process import app
from global_vars import config  # import đúng chỗ

async def main():
    tasks = [
        asyncio.create_task(server_process()),
        asyncio.create_task(run_quart_https())
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cancelling tasks...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
    finally:
        print("Program exited cleanly.")

async def run_quart_https():
    hyper_config = Config()
    hyper_config.bind = [f"0.0.0.0:{config['http_interface']['secure_port']}"]
    hyper_config.certfile = "/home/admin/.acme.sh/vietbot.vn_ecc/fullchain.cer"
    hyper_config.keyfile = "/home/admin/.acme.sh/vietbot.vn_ecc/vietbot.vn.key"
    
    await hypercorn.asyncio.serve(app, hyper_config)

if __name__ == "__main__":
    asyncio.run(main())
