import docker
import time

# Mapa portów dla Twoich usług
SERVICE_URLS = {
    "PIHOLE": "http://192.168.1.15:8080/admin",  # Zmień na IP swojego PC
    "PORTAINER": "https://192.168.1.15:9443",
    "PROXY": "http://192.168.1.15:81"
}


def get_docker_stats():
    start_time = time.time()
    stacks = {}
    try:
        client = docker.from_env()
        for container in client.containers.list(all=True):
            raw_name = container.labels.get('com.docker.compose.project') or container.name
            name = raw_name.split('_')[0].split('-')[0].upper()

            if name not in stacks:
                stacks[name] = {
                    "name": name,
                    "count": 0,
                    "running": 0,
                    "url": SERVICE_URLS.get(name, "#")  # Pobiera link z mapy wyżej
                }

            stacks[name]["count"] += 1
            if container.status == 'running':
                stacks[name]["running"] += 1

        ping = f"{round((time.time() - start_time) * 1000)}ms"
        return {"stacks": list(stacks.values()), "ping": ping}
    except Exception as e:
        return {"stacks": [], "ping": "error"}