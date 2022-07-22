from typing import Dict, List
from uuid import uuid4

import httpx

# Protocol (http or https) and host of server
SERVER_URL = "http://localhost"
# Server port (80 is standard web, 443 is secure web (https), 8000 is common for local
# development)
SERVER_PORT = 8000
# Must match nginx.conf location for allowing uploads
SERVER_UPLOAD_PREFIX = "uploads"


def _request(method: str, path: str, **kwargs) -> httpx.Response:
    """Main method for sending requests to the nginx file server"""

    with httpx.Client() as client:
        res = client.request(
            method.upper(),
            f"{SERVER_URL}:{SERVER_PORT}/{path}",
            **kwargs,
        )
    res.raise_for_status()
    return res


def ls(path: str = "/") -> List[Dict[str, str]]:
    """List directories on nginx file server

    Parameters:
        path: Optional filepath.
    """
    if not path.endswith("/"):
        path += "/"

    req = _request("GET", path)
    return req.json()


def get(path: str) -> bytes:
    """Retrieve file from nginx file server

    Parameters:
        path: Full filepath to the file to download. Does not begin with '/'.

    Returns:
        Bytes of the file. All files (text or binary) returned as bytes. So to
        write to disk open file in binary mode. e.g.,:
            with open('my_output.txt', 'wb') as f:
                f.write(client.get('path_to_file'))
    """
    req = _request("GET", path)
    return req.content


def put(filename: str, content: bytes) -> str:
    """Upload a file to the nginx file server

    Returns:
        Path to the uploaded file.
        NOTE: Full path will vary from filename passed as server will place file
            into designated uploads directory with uuid in path.
    """
    # NOTE: Am using uuid() so that if diverse clients upload a file with the same name
    # it doesn't overwrite other files. Every file will have a unique filename.
    uuid = uuid4()
    req = _request("PUT", f"{SERVER_UPLOAD_PREFIX}/{uuid}-{filename}", content=content)
    return str(req.url.path)[1:]  # remove intial '/'


if __name__ == "__main__":
    # From the command line to upload files you can use this script like:
    # python client.py myfilename.whatever /path/to/myfile.whatever
    import sys

    upload_name = sys.argv[1]
    path = sys.argv[2]

    with open(path, "rb") as f:
        data = f.read()
        put(upload_name, data)
