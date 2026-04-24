import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.bom_tools import build_bom_json


@dataclass(frozen=True)
class BomAgentWorkflow:
    timeout_s: int = 20
    headers: dict[str, str] | None = None

    def run(self, url: str) -> dict[str, Any]:
        return build_bom_json(url, timeout_s=self.timeout_s, headers=self.headers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    workflow = BomAgentWorkflow()
    result = workflow.run(args.url)
    text = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
