import importlib.util
import sys
from pathlib import Path

from uranium.console import Console
from uranium.errors import UraniumError
from uranium.interpreter import Interpreter


def load_builtin_module(path):
    spec = importlib.util.spec_from_file_location(f"uranium_builtin_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect_builtins():
    builtin_directory = Path(__file__).parent / "built-in"
    functions = load_builtin_module(builtin_directory / "functions.py")
    classes = load_builtin_module(builtin_directory / "classes.py")
    return {**getattr(functions, "FUNCTIONS", {}), **getattr(classes, "CLASSES", {})}


def run_file(path, interpreter):
    source = Path(path).read_text(encoding="utf-8")
    try:
        interpreter.run_source(source)
    except UraniumError as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 1
    return 0


def main():
    interpreter = Interpreter(collect_builtins())
    if len(sys.argv) > 1:
        return run_file(sys.argv[1], interpreter)
    return Console(interpreter).run()


if __name__ == "__main__":
    sys.exit(main())
