"""Publish the already-rendered _book/ to Quarto Pub using curl for the HTTP calls.

`quarto publish quarto-pub --no-render --no-prompt` is the normal route. In a
cloud session behind a network proxy, the tool's own requests can fail (uploads
of image files, some status checks), so this script repeats the same API calls
with curl: create a deploy, upload the files the server asks for, wait until
ready, update the account page. Run it from the book directory.

Needs _publish.yml (site id) and a Quarto Pub token. The token is read from
QUARTO_PUB_AUTH_TOKEN if set; behind a proxy that injects it, leave it unset.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

API = "https://quartopub.com/api/v1/"
site_id = re.search(r"id:\s*([0-9a-f-]+)", open("_publish.yml").read()).group(1)
token = os.environ.get("QUARTO_PUB_AUTH_TOKEN")
auth = ["-H", f"Authorization: Bearer {token}"] if token else []


def call(method, path, *extra):
    r = subprocess.run(["curl", "-sS", "--max-time", "120", "-X", method, API + path,
                        "-H", "Accept: application/json", *auth, *extra, "-w", "\n%{http_code}"],
                       capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    return int(code or 0), body


files = {}
size = 0
for root, _, names in os.walk("_book"):
    for n in names:
        p = os.path.join(root, n)
        rel = os.path.relpath(p, "_book").replace(os.sep, "/")
        data = open(p, "rb").read()
        size += len(data)
        files[rel] = hashlib.sha1(data).hexdigest()

payload = json.dumps({"size": size, "files": {"/" + k: v for k, v in files.items()}})
code, body = call("POST", f"sites/{site_id}/deploys", "-H", "Content-Type: application/json", "--data-binary", payload)
if code not in (200, 201):
    sys.exit(f"could not create deploy: HTTP {code} {body[:200]}")
deploy = json.loads(body)
while deploy.get("state") not in ("prepared", "ready"):
    time.sleep(0.5)
    deploy = json.loads(call("GET", f"deploys/{deploy['id']}")[1])
required = set(deploy.get("required") or [])
todo = [k for k, v in files.items() if v in required]
print(f"{len(files)} files in the book; {len(todo)} to upload")
for k in todo:
    for attempt in range(4):
        code, body = call("PUT", f"deploys/{deploy['id']}/files/{urllib.parse.quote(k)}",
                          "-H", "Content-Type: application/octet-stream", "--data-binary", "@" + os.path.join("_book", k))
        if code in (200, 201):
            break
        time.sleep(2)
    else:
        sys.exit(f"upload failed for {k}: HTTP {code} {body[:200]}")
    print("  uploaded", k)
for _ in range(240):
    d = json.loads(call("GET", f"deploys/{deploy['id']}")[1])
    if d.get("state") == "ready":
        print("ready:", d.get("url"))
        break
    time.sleep(0.5)
else:
    sys.exit("deploy did not become ready")
code, body = call("PUT", "update-account-site")
print("account page:", body[:120] if code in (200, 201) else f"not updated (HTTP {code})")
print("A new site can take a minute or two to start serving. Poll the public address; do not re-publish.")
