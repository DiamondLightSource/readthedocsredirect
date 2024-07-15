import argparse
from typing import Set
import requests
import re

parser = argparse.ArgumentParser(
    description="Setup a redirect from readthedocs to github.io"
)
parser.add_argument("project", help="Name of the project_slug on readthedocs")
parser.add_argument(
    "repo", help="Name of the repo name on GitHub, defaults to <project>", nargs="?"
)
parser.add_argument(
    "--org",
    help="Name of the organization name on GitHub, defaults to DiamondLightSource",
    default="DiamondLightSource",
)
args = parser.parse_args()

if args.repo is None:
    args.repo = args.project

class Redirecter:
    TOKEN = open("/dls_sw/prod/etc/tokens/readthedocs.token").read().strip()
    HEADERS = dict(Authorization=f"token {TOKEN}")
    TO_URL_FORMAT = r"/\w+/(\w+)/\$rest"


    def __init__(self, org: str, repo: str, project):

        self.project = project
        self.github_url = f"https://{org}.github.io/{repo}/master/"
        self.project_url = f"https://readthedocs.org/api/v3/projects/{project}"
        self.read_the_docs_url = f"https://{project}.readthedocs.io"

    def link_project_to_github(self):
        data= {
            "default_branch": self.project,
            "repository": {"url":  "https://github.com/DiamondLightSource/readthedocsredirect"},
            "homepage": self.github_url,
        }

        response = requests.patch(
            self.project_url,
            json=data,
            headers=self.HEADERS,
        )
        assert response.ok

    def check_redirects(self) -> Set[str]:
        """
        Checks for redirects already set up through this script.
        Errors if redirects are present which aren't expected
        """

        response = requests.get(
            f"{self.project_url}/redirects/",
            headers=self.HEADERS
        )
        assert response.ok, response.json()

        already_redirected = set()

        for redirect in response.json()["results"]:
            match = re.match(self.TO_URL_FORMAT, redirect["from_url"])
            if redirect["to_url"] != self.github_url or not match:
                raise RuntimeError(
                    "Project contains an unknown redirect "
                    f"{redirect['from_url']} to {redirect['to_url']}. "
                    "Delete it before proceeding."
                )

            version_name = match.group(1)
            already_redirected.add(version_name)

        return already_redirected

    def get_active_versions(self) -> Set[str]:
        # Set a redirect on all active versions
        response = requests.get(
            f"{self.project_url}/versions", headers=self.HEADERS
        )
        assert response.ok, response.json()
        versions = response.json()["results"]

        return set(version["verbose_name"] for version in versions if version["active"])

    def set_up_redirects_on_versions(self, versions: Set[str]):
        for version_name in versions:
            # Setup a redirect for 
            response = requests.post(
                f"{self.project_url}/redirects/",
                json=dict(from_url=f"/en/{version_name}/$rest", to_url=self.github, type="exact"),
                headers=self,
            )
            assert response.ok, response.json()

    def redirect(self):
        print(f"beginning reconfiguration of readthedocs project {self.project}")
        self.link_project_to_github()
        print("success")
        active_versions = self.get_active_versions()
        print("active versions of project:")
        for version in active_versions:
            print(f"    {version}")

        already_redirected_versions = self.check_redirects()

        versions_to_redirect = active_versions.difference(already_redirected_versions)

        if not versions_to_redirect:
            print("redirects are already set up for every active version")
            return

        if already_redirected_versions:
            print("will skip redirects already set up:")
            for version in already_redirected_versions:
                print(f"    {version}")

        print("setting up redirects")
        self.set_up_redirects_on_versions(versions_to_redirect)
        print("success")

        if "latest" in versions_to_redirect:
            print("'latest' was redirected, rebuilding it")
            response = requests.post(
                f"{self.project_url}/versions/latest/builds/",
                headers=self.HEADERS,
            )
            assert response.ok, response.json()

        print(f"{self.read_the_docs_url} should soon redirect to {self.github_url}")


Redirecter(args.org, args.repo, args.project).redirect()
