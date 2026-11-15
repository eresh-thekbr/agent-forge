import argparse

from .knowledge import FACTS, describe
from .workflow import build_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Who works on projects that use a technology?")
    parser.add_argument("--technology", default="Python")
    args = parser.parse_args()
    print("KNOWLEDGE GRAPH — stored facts")
    for fact in FACTS:
        print(f"  {describe(fact)}")
    print(f"\nQUESTION — Who works on projects that use {args.technology}?")
    print("\nLANGGRAPH — workflow steps and state updates")
    for update in build_workflow().stream({"technology": args.technology}, stream_mode="updates"):
        for step, values in update.items():
            print(f"  {step}: {values}")
            if "answer" in values:
                print(f"\nANSWER — {values['answer']}")


if __name__ == "__main__":
    main()
