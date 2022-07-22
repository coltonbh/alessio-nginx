# Alessio Nginx

A simple file server than can accept uploads. Built with ❤️ for Alessio.

## Usage

### Create and source a virtual environment using python 3.7+

```sh
python -m venv env
source ./env/bin/activate
```

### Install necessary package(s)

```sh
pip install -r requirements.txt
```

### Manage Configuration

1. Set global variables in `client.py` as needed. The default values will work fine for local development

```sh
SERVER_URL = "http://localhost"
SERVER_PORT = 8000
SERVER_UPLOAD_PREFIX = "uploads"
```

2. Determine whether nginx will serve `html` (human readable) or `json` (machine readable) data. The `autoindex_format` value can be set independently for both the `/` and `/uploads/` locations. The `put()` and `get()` methods will work with either setting, the `ls()` method will only work if serving `json`. If you change these values you'll need to stop and restart your server to load the new configuration.

### Start the file server.

Note that nginx is running as `root` inside the docker container so the files it writes to your system will be owned by `root`. In practice, you'd probably want to mount a docker [volume](https://docs.docker.com/storage/volumes/) rather than the `./shared_files` directory into the container. However, using a local directory makes it easier to see what's going on.

```sh
# Omit the -d if you want to run the server in the foreground to see logs
docker-compose up -d
```

Go to <http://localhost:8000> to view your server.

### Work with the client

```python
# From the root directory of this project
>>> import client

>>> client.ls()
# Open file in binary mode and load bytes to the server
>>> with open("path_to_some_file", "rb") as f:
        data = f.read()
        url = client.put("my_filename.whatever", data)
>>> url
'uploads/62b2013b-097e-4560-9119-449650dca77c-my_filename.whatever'

# Download the file I just uploaded
>>> data = client.get(url)
>>> with open("my_ouput_file.whatever", "wb") as f:
        f.write(data)

```

### Upload files from the command line

Generally:

```sh
python client.py mynewfilename.whatever /path/to/file/i/want/to/upload/file.whatever
```

For example:

```sh
python client.py new-docker-compose.yaml ./docker-compose.yaml
```

Now check the `/uploads/` directory of your file server and the local `shared_files` directory.

### Shut things down

Stop web server:

```sh
docker-compose down
```

Deactivate python virtual environment:

```sh
deactivate
```

Remove `shared_files` directory:

```sh
# Need sudo because files were written by nginx running as root
sudo rm -rf shared_files
```

### Deployment

Deploy this service behind a [traefik](https://traefik.io/) reverse proxy that provides `TLS`, `http` -> `https` redirects, etc. for a secure production deployment. See [Docker Swarm Rocks](https://dockerswarm.rocks/) for a great overview.

## Further Research

This project is built on the built-in nginx module [ngx_http_dav_module](https://nginx.org/en/docs/http/ngx_http_dav_module.html). It is using the WebDAV protocol to allow basic HTTP methods like `PUT` and `DELETE`. Other methods can be added if needed. Google `nginx webdav` to find examples and more details.
