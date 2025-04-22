from lib_process import asyncio, ssl, config  # bỏ global_vars nếu không cần
from server_process import start_audio_server

from api_process import app


if config['http_interface']['mode'] =='secure':
    import hypercorn.asyncio
    from hypercorn.config import Config
    async def run_quart_https():
        hyper_config = Config()
        hyper_config.bind = [f"0.0.0.0:{config['http_interface']['secure_port']}"]
        hyper_config.certfile = "/home/admin/.acme.sh/vietbot.vn_ecc/fullchain.cer"
        hyper_config.keyfile = "/home/admin/.acme.sh/vietbot.vn_ecc/vietbot.vn.key"
        
        await hypercorn.asyncio.serve(app, hyper_config)


async def main():

    if config['http_interface']['mode'] =='secure':
        tasks = [
            asyncio.create_task(start_audio_server()),
            asyncio.create_task(run_quart_https())
        ]
    else:
        tasks = [
            asyncio.create_task(start_audio_server()),
            asyncio.create_task(app.run_task(host="0.0.0.0", port=config["http_interface"]['port']))  
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


if __name__ == "__main__":
    asyncio.run(main())
