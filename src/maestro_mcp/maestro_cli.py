import os.path
import shutil
import subprocess
import tempfile
import requests
from .logger import get_logger

logger = get_logger("maestro_cli")


class MaestroCli:
    def __init__(
            self,
            api_key: str = None,
            maestro_binary_path: str = None,
            api_server: str = "https://api.copilot.mobile.dev"
    ):
        self.api_server = api_server
        # validate if maestro is in path
        try:
            self.maestro_binary_path = maestro_binary_path or shutil.which("maestro")
            if self.maestro_binary_path is None or not self.maestro_binary_path:
                if os.path.exists(os.path.join(os.path.expanduser("~/.maestro"), "bin", "maestro")):
                    self.maestro_binary_path = os.path.join(os.path.expanduser("~/.maestro"), "bin", "maestro")
                    logger.info("maestro binary found at default location %s", self.maestro_binary_path)
                else:
                    logger.info("maestro binary not found in path!")
            else:
                self.maestro_binary_path = os.path.abspath(os.path.expanduser(self.maestro_binary_path))
                logger.info("maestro binary found at %s", self.maestro_binary_path)
        except Exception as e:
            logger.error("maestro binary not found in path - %s", e)

        self.api_key = api_key
        if api_key is None:
            try:
                home_dir = os.path.expanduser("~")
                with open(os.path.abspath(os.path.join(home_dir, ".mobiledev", "authtoken")), "r") as f:
                    logger.info("maestro api key found at %s",
                                os.path.abspath(os.path.join(home_dir, ".mobiledev", "authtoken")))
                    self.api_key = f.read().strip()
            except Exception as e:
                logger.error(
                    "maestro api key not found, please install it following the instructions at https://docs.maestro.dev/getting-started/installing-maestro and login with maestro login")

    def _respond(self, res) -> str:
        if res.stderr:
            logger.error(res.stderr)
            raise Exception(res.stderr)
        logger.info(res.stdout)
        return res.stdout.strip()

    def _check_cli(self):
        if self.maestro_binary_path is None or not self.maestro_binary_path:
            raise RuntimeError(
                "Maestro CLI not found on path - please install it following the instructions at https://docs.maestro.dev/getting-started/installing-maestro and make sure it's in your PATH, or use the MAESTRO_BINARY_PATH environment variable")

        if self.api_key is None:
            raise RuntimeError(
                "Maestro API key not found - please supply one with the MAESTRO_API_KEY environment variable or use `maestro login` to log in to your maestro account")

    def check_syntax(self, code) -> str:
        self._check_cli()

        with tempfile.NamedTemporaryFile("w") as f:
            f.write(code)
            f.flush()

            # shell out to maestro cli
            res = subprocess.run(
                [self.maestro_binary_path, "check-syntax", f.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return self._respond(res)

    def run_code(self, code) -> str:
        if "---" not in code:  # no header present
            code = "appId: any\n---\n" + code

        lines = code.split("\n")
        header_index = lines.index("---")

        # Keep header as is, process commands after the header
        header = lines[:header_index + 1]
        commands = lines[header_index + 1:]

        # Process each command line
        processed_commands = []
        for line in commands:
            if line.strip() and not line.startswith(" ") and not line.startswith("- "):
                processed_commands.append("- " + line)
            else:
                processed_commands.append(line)

        code = "\n".join(header + processed_commands)

        sc = self.check_syntax(code)
        if sc != 'OK':
            return sc

        with tempfile.NamedTemporaryFile("w") as f:
            f.write(code)
            f.flush()

            # shell out to maestro cli
            res = subprocess.run(
                [self.maestro_binary_path, "test", "--reinstall-driver=false", f.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return self._respond(res)

    def run_test(self, flow_files):
        self._check_cli()

        res = subprocess.run(
            [self.maestro_binary_path, "test", "--reinstall-driver=false", flow_files],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        return self._respond(res)

    def get_hierarchy(self) -> str:
        self._check_cli()
        res = subprocess.run(
            [self.maestro_binary_path, "hierarchy", "--reinstall-driver=false", "--compact=true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        return self._respond(res)

    def start_device(self, os, platform):
        self._check_cli()

        res = subprocess.run(
            [self.maestro_binary_path, "start-device", "--os-version", os, "--platform", platform],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        return self._respond(res)

    def cheat_sheet(self) -> str:
        self._check_cli()

        res = requests.get(
            f"{self.api_server}/v2/bot/maestro-cheat-sheet",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        if res.status_code != 200:
            raise Exception(f"Failed to get cheat sheet - {res.status_code} {res.text}")

        return res.text

    def query_docs(self, question) -> str:
        self._check_cli()

        # POST https://api.copilot.mobile.dev/v2/bot/query-docs with { question: string }
        question = f"""Search the Maestro documentation to answer the following question:\n{question}\nAlways try to include examples on your responses. No need to include links to documentation."""

        res = requests.post(
            f"{self.api_server}/v2/bot/query-docs",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"question": question},
        )
        if res.status_code != 200:
            raise Exception(f"Failed to query docs - {res.status_code} {res.text}")

        return res.json()["answer"]
