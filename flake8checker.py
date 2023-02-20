import ast
import logging
import re

logger = logging.getLogger(__name__)


class LogFormattingChecker(ast.NodeVisitor):
    name = "flake8-log-formatting"
    version = "0.2.0"

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.tree = tree
        self.filename = filename
        self.errors = []

    def run(self) -> list[tuple[int, int, str]]:
        logger.debug("Running Flake8 plugin %s on file %s", self.name,
                     self.filename)
        self.visit(self.tree)
        logger.debug("Flake8 plugin %s found %d errors in file %s", self.name,
                     len(self.errors), self.filename)
        return self.errors

    def visit_Call(self, node: ast.Call) -> None:
        logger.debug("Visiting call node: %s", ast.dump(node))
        if not isinstance(node.func, ast.Attribute):
            return
        attr = node.func
        if not isinstance(attr.value, ast.Name):
            return
        method_name = attr.attr
        if method_name not in {
                "debug",
                "info",
                "warning",
                "error",
                "exception",
                "critical",
        }:
            return
        format_str = None
        for keyword in node.keywords:
            if keyword.arg == 'msg':
                msg_arg = keyword.value
                if isinstance(msg_arg, ast.Str):
                    format_str = msg_arg.s
                    break
        if not format_str:
            for arg in node.args:
                if isinstance(arg, ast.Str):
                    format_str = arg.s
                    break
        if not format_str:
            return
        expected_count = len(re.findall(r"%[sdf]", format_str))
        actual_count = len(node.args)
        if format_str is not None and 'msg' not in [
                keyword.arg for keyword in node.keywords
        ]:
            actual_count -= 1
        if expected_count != actual_count:
            lineno = node.lineno
            col_offset = node.col_offset
            adjective = 'few' if actual_count < expected_count else 'many'
            message = f"LOG001 Too {adjective} arguments for format string"
            # I don't know why None is required, but flake8 expects 4 arguments
            # and immidiately discards the fourth chat gpt thought it'd be fine
            # with three
            self.errors.append((lineno, col_offset, message, None))
            logger.debug("Found error at line %d: %s", lineno, message)


def run_flake8_plugin(tree: ast.AST,
                      filename: str) -> list[tuple[int, int, str]]:
    checker = LogFormattingChecker(tree, filename)
    return checker.run()
