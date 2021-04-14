

import requests

import argparse

parser = argparse.ArgumentParser(description="Setup a redirect from readthedocs to github.io")
parser.add_argument('project', help="Name of the project_slug on readthedocs")
parser.add_argument('repo', help="Name of the repo name on GitHub, defaults to <project>", nargs="?")
parser.add_argument('--org', help="Name of the organization name on GitHub, defaults to dls-controls", default="dls-controls")
args = parser.parse_args()

if args.repo is None:
    args.repo = args.project

TOKEN = open("/dls_sw/prod/etc/tokens/readthedocs.token").read().strip()
HEADERS = dict(Authorization= f'token {TOKEN}')
github = f"https://{args.org}.github.io/{args.repo}/master/"

# Change the URL
response = requests.get(
    f"https://readthedocs.org/api/v3/projects/{args.project}/",
    headers=HEADERS
)
assert response.ok, response.json()
data = response.json()
del data["language"]
del data["programming_language"]
data["repository"]["url"] = "https://github.com/dls-control/readthedocsredirect"
data["homepage"] = github
response = requests.patch(
    f"https://readthedocs.org/api/v3/projects/{args.project}/",
    json=data,
    headers=HEADERS,
)
assert response.ok, response.json()

# Setup a redirect
response = requests.post(
    f"https://readthedocs.org/api/v3/projects/{args.project}/redirects/",
    json=dict(from_url="/en/latest/$rest", to_url=github, type="exact"),
    headers=HEADERS,
)
assert response.ok, response.json()

print(f"https://{args.project}.readthedocs.io should now redirect to {github}")
