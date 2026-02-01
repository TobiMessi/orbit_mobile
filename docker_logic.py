import httpx
import time

async def ping_server(server_ip, server_port=5001):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"http://{server_ip}:{server_port}/status"
            response = await client.get(url)
            if response.status_code == 200:
                ping = f"{round((time.time() - start_time) * 1000)}ms"
                return {"connected": True, "ping": ping}
            return {"connected": False, "ping": "err"}
    except Exception:
        return {"connected": False, "ping": "err"}

async def get_docker_stats(server_ip, server_port=5001):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"http://{server_ip}:{server_port}/status"
            response = await client.get(url)
            data = response.json()
            
            ping = f"{round((time.time() - start_time) * 1000)}ms"
            
            return {
                "stacks": data.get("stacks", []),
                "containers": data.get("containers", []),
                "images": data.get("images", []),
                "volumes": data.get("volumes", []),
                "networks": data.get("networks", []),
                "counts": data.get("counts", {}),
                "ping": ping,
                "connected": True
            }
    except Exception as e:
        return {
            "stacks": [],
            "containers": [],
            "images": [],
            "volumes": [],
            "networks": [],
            "counts": {"containers": 0, "images": 0, "volumes": 0, "networks": 0, "stacks": 0},
            "ping": "error",
            "connected": False,
            "error": str(e)
        }

async def container_action(server_ip, server_port, container_id, action):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"http://{server_ip}:{server_port}/container/{container_id}/{action}"
            response = await client.post(url)
            return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def stack_action(server_ip, server_port, stack_name, action):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            url = f"http://{server_ip}:{server_port}/stack/{stack_name}/{action}"
            response = await client.post(url)
            return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
