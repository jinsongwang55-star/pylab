import io
import logging
from contextlib import redirect_stdout
from pathlib import Path

import solution
from _harness import run


def _reset():
    """清掉全局 logger 的 handler，避免测试之间互相污染。"""
    logger = logging.getLogger("task")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


def test_identity():
    _reset()
    logger = solution.setup_logger(Path("l1.log"))
    assert logger.name == "task", f"logger 名字应为 task，实际 {logger.name}"
    assert logger.propagate is False, "propagate 必须为 False"


def test_file_gets_debug_with_format():
    _reset()
    path = Path("l2.log")
    if path.exists():
        path.unlink()
    logger = solution.setup_logger(path)
    logger.debug("调试信息")
    logger.info("普通信息")
    content = path.read_text(encoding="utf-8")
    assert "DEBUG|调试信息" in content, f"文件缺少 DEBUG 行: {content!r}"
    assert "INFO|普通信息" in content, f"文件缺少 INFO 行: {content!r}"


def test_console_default_level():
    _reset()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        logger = solution.setup_logger(Path("l3.log"))
        logger.debug("不应出现")
        logger.info("应该出现")
    out = buffer.getvalue()
    assert "应该出现" in out, f"INFO 应输出到控制台: {out!r}"
    assert "不应出现" not in out, f"默认控制台级别为 INFO，DEBUG 不应输出: {out!r}"


def test_console_verbose():
    _reset()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        logger = solution.setup_logger(Path("l4.log"), verbose=True)
        logger.debug("调试可见")
    assert "调试可见" in buffer.getvalue(), "verbose=True 时控制台应输出 DEBUG"


def test_no_duplicate_handlers():
    _reset()
    solution.setup_logger(Path("l5a.log"))
    logger = solution.setup_logger(Path("l5b.log"))
    assert len(logger.handlers) == 2, f"重复配置后应仍为 2 个 handler，实际 {len(logger.handlers)}"
    logger.info("新文件")
    content = Path("l5b.log").read_text(encoding="utf-8")
    assert "新文件" in content, "第二次配置应指向新的日志文件"


def test_no_duplicate_console_lines():
    _reset()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        logger = solution.setup_logger(Path("l6.log"))
        logger.info("只应出现一次")
    assert buffer.getvalue().count("只应出现一次") == 1, "日志被重复输出，说明 handler 叠加了"


run([
    ("logger 名称与 propagate", test_identity),
    ("文件记录 DEBUG 且格式正确", test_file_gets_debug_with_format),
    ("控制台默认 INFO 级别", test_console_default_level),
    ("verbose 输出 DEBUG", test_console_verbose),
    ("重复调用不叠加 handler", test_no_duplicate_handlers),
    ("控制台不重复输出", test_no_duplicate_console_lines),
])
