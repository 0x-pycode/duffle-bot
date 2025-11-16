# core/account.py

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Account:
    """
    Represents a Duffle/Twitter account structure.
    """
    acc_name: str
    email: str
    privi_ca: str
    twitter_username: str
    ref_code: str
    proxy: Optional[Dict[str, str]] = None

    def __repr__(self):
        return f"<Account {self.acc_name}>"

    def get_proxy_string(self) -> Optional[str]:
        """
        Returns proxy like user:pass@host:port
        """
        if not self.proxy:
            return None

        host = self.proxy.get("proxy_host")
        port = self.proxy.get("proxy_port")
        login = self.proxy.get("login")
        password = self.proxy.get("passwd")

        if not all([host, port, login, password]):
            return None

        return f"{login}:{password}@{host}:{port}"

    def get_proxy_dict(self) -> Dict[str, str]:
        proxy_str = self.get_proxy_string()
        if proxy_str:
            return {
                "http": f"http://{proxy_str}",
                "https": f"http://{proxy_str}"
            }
        return {}

    def get_proxy_part(self):
        if not self.proxy:
            return [None, None, None, None]
        return [
            self.proxy.get("proxy_host"),
            self.proxy.get("proxy_port"),
            self.proxy.get("login"),
            self.proxy.get("passwd")
        ]


class Colors:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
