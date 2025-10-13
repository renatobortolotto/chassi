from atomic import Environments

envs = Environments()
prefix = envs.get_env("SERVER_ROOT", "/api")
host = envs.get_env("HOST", "127.0.0.1")
port = envs.get_env("PORT", 8080)
