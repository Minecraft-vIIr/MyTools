import requests
import base64
import os
import json

def upload_file(file_path, token, user, repo, remote_path, message="", committer="anonymous", email="anonymous@gmail.com"):
    try:
        with open(file_path, "rb+") as f:
            file_data = f.read()
    except Exception as err:
        return False

    file_name = os.path.basename(file_path)
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{remote_path}" + file_name
    headers = {"Authorization": "token " + token}
    content = base64.b64encode(file_data).decode("utf-8")
    data = {
        "message": message,
        "committer": {
            "name": committer,
            "email": email
        },
        "content": content
    }
    data = json.dumps(data)
    try:
        req = requests.put(url=url, data=data, headers=headers)
        req.encoding = "utf-8"
        re_data = json.loads(req.text)
    except Exception as err:
        return False

    if "content" in re_data:
        return re_data
    else:
        return False


def download_file(remote_file_path, token, user, repo, local_path):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{remote_file_path}"
    headers = {"Authorization": "token " + token, "Accept": "application/vnd.github.v3.raw"}

    try:
        response = requests.get(url, headers=headers, stream=True)
    except Exception as err:
        return False

    if response.status_code == 200:
        try:
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024): 
                    if chunk:
                        f.write(chunk)
        except Exception as err:
            return False
        return True
    else:
        return False

def list_files(remote_path, token, user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{remote_path}"
    headers = {"Authorization": "token " + token}

    try:
        response = requests.get(url, headers=headers)
    except Exception as err:
        return False

    if response.status_code == 200:
        files = response.json()
        file_paths = []
        for file in files:
            if file["type"] == "dir":
                file_paths.extend(list_files(file["path"], token, user, repo))
            else:
                file_paths.append(file["path"])
        return file_paths
    else:
        return False

def delete_file(remote_path, token, user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{remote_path}"
    headers = {"Authorization": "token " + token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sha = response.json()["sha"]

        data = {
            "message": f"delete {remote_path}",
            "sha": sha
        }
        response = requests.delete(url, headers=headers, json=data)
        response.raise_for_status()
    except Exception as err:
        return False

    return True
