# PyLab · Python 学习与验证平台

本地运行的交互式学习系统：左侧课程目录，中间正文，右侧代码编辑器。
每道练习都在独立临时目录中执行并由隐藏测试自动判定，进度保存在本地。

纯 Python 标准库实现，**没有任何第三方依赖**，不需要虚拟环境。

## 启动

```bash
cd python-learn
python3 server.py
```

浏览器会自动打开 `http://127.0.0.1:8000/`。如果端口被占用会自动顺延，也可以用：

```bash
python3 server.py --port 8100   # 指定端口
python3 server.py --no-open     # 不自动打开浏览器
```

要求 Python 3.10+（使用了 `X | None` 类型语法与 `Path.is_relative_to`）。

## 在线运行（GitHub Codespaces）

https://codespaces.new/jinsongwang55-star/pylab

打开后容器会自动执行 `postStartCommand` 启动服务。在 Ports 面板找到 8000 端口，选择「Open in Browser」即可开始练习。首次启动容器需要一两分钟。

注意：它不是 GitHub Pages。判题需要执行 Python 代码，必须运行在容器或服务器里，静态托管做不到。

## 桌面快捷方式

项目内自带启动脚本：

- Linux / macOS：`./launch.sh`
- Windows：双击 `launch.bat`

想在桌面生成一个双击即用的图标：

```bash
python3 make_shortcut.py
```

脚本会按当前系统创建对应快捷方式：

| 系统 | 生成文件 | 行为 |
|---|---|---|
| Linux | `~/Desktop/PyLab.desktop` | 无终端窗口，后台启动 |
| macOS | `~/Desktop/PyLab.app` | 无终端窗口，Dock 不显示图标 |
| Windows | `~/Desktop/PyLab.vbs` | 完全隐藏 cmd 窗口 |

三个平台都是静默启动：日志写入 `data/server.log`，出错时 Linux 用 `notify-send`、macOS 用 `osascript` 发桌面通知。

macOS 的 `PyLab.app` 是最小应用包（`Contents/Info.plist` + `Contents/MacOS/PyLab`），`LSUIElement=true` 让它不占 Dock。它未经签名与公证，首次打开若提示「无法验证开发者」，右键点击图标选「打开」即可，或执行：

```bash
xattr -dr com.apple.quarantine ~/Desktop/PyLab.app
```

快捷方式记录的是**当前项目绝对路径**。移动 `python-learn` 目录后，重新运行一次 `make_shortcut.py`。

## 停止服务

```bash
./stop.sh     # Linux / macOS
stop.bat      # Windows
```

静默启动后没有终端窗口可关，用上面的命令停止。服务启动时会把 PID 写入 `data/server.pid`、实际端口写入 `data/server.port`，停止后自动清理。重复启动不会产生第二个实例，而是直接打开已运行实例的地址。

## 怎么学

1. 读正文，把示例代码复制到编辑器改参数运行
2. 做练习，点「检查」逐条看测试结果
3. 全绿后进入下一课
4. 第二天不看资料重写昨天的练习

快捷键：`Ctrl+Enter` 运行，`Ctrl+Shift+Enter` 检查。

代码草稿按课程分别存在浏览器 `localStorage`，换课不会丢；点「重置」恢复起始代码。

卡住超过 20 分钟可以点「参考答案」，但看完必须关掉，凭记忆重写一遍。

## 当前内容

**阶段 1 · 语法唤醒**（8 节课 / 7 组练习 / 40 个测试用例）

| 课程 | 练习 |
|---|---|
| 1.0 导览：这套系统怎么用 | 无 |
| 1.1 数值与类型：金额为什么不能用 float | `parse_amount`，8 项 |
| 1.2 容器与推导式：选对数据结构 | `summarize_tags`，5 项 |
| 1.3 函数与作用域：闭包与可变默认参数 | `make_counter` / `append_item`，5 项 |
| 1.4 装饰器：不改原函数的增强 | `log_calls`，5 项 |
| 1.5 生成器：惰性求值 | `fib` / `take`，5 项 |
| 1.6 异常与上下文管理器 | `atomic_json`，5 项 |
| 1.7 综合实战：带持久化的记账核心 | `Ledger`，7 项 |

**阶段 2 · 标准库实战**（5 节课 / 5 组练习 / 29 个测试用例）

| 课程 | 练习 |
|---|---|
| 2.0 pathlib：路径不是字符串 | `classify_files`，6 项 |
| 2.1 正则：从文本里精确取数 | `parse_log_line` / `mask_phones`，6 项 |
| 2.2 logging：把 print 换掉 | `setup_logger`，6 项 |
| 2.3 argparse：命令行接口 | `build_parser`，5 项 |
| 2.4 综合：可撤销的文件整理器 | `organize` / `undo`，6 项 |

阶段 2 的完整任务书在 `../python-reboot/stage2-stdlib/README.md`。

**阶段 3 · 工程化**（5 节课 / 4 组练习 / 22 个测试用例）

| 课程 | 练习 |
|---|---|
| 3.0 类型提示：把契约写进代码 | `TypedDict` + `adult_names`，6 项 |
| 3.1 dataclass：数据不是字典 | 冻结 `Item` + 校验，6 项 |
| 3.2 纯函数与依赖注入：让时间可控 | 过期判断与汇总，5 项 |
| 3.3 工具链：pytest / ruff / CI | 无判题，需在真实仓库完成 |
| 3.4 综合：可测试的重试策略 | `RetryPolicy.run`，5 项 |

**阶段 4 · 异步与并发**（5 节课 / 4 组练习 / 21 个测试用例）

| 课程 | 练习 |
|---|---|
| 4.0 协程与并发：gather 的正确用法 | `fetch_all`，5 项 |
| 4.1 并发上限：Semaphore | `fetch_limited`，5 项 |
| 4.2 超时与失败隔离 | `fetch_with_timeout` / `collect`，5 项 |
| 4.3 httpx 实战与本地模拟服务 | 无判题，需本机装 httpx 完成自查 |
| 4.4 综合：带重试的批量抓取器 | `crawl`，6 项 |

阶段 4 的判题不访问外网：测试注入 `exercises/_mock_service.py` 提供的本地异步模拟服务，延迟、失败次数、挂起行为都可精确控制，因此可以稳定断言并发峰值与超时行为。真实 httpx 抓取在 4.3 用本地 `mock_server.py` 自查。

**阶段 5 · Web 后端**（5 节课 / 4 组练习 / 28 个测试用例）

| 课程 | 练习 |
|---|---|
| 5.0 路由：方法、路径与参数 | `Router`，7 项 |
| 5.1 请求校验：把非法数据挡在门口 | `validate_user`，7 项 |
| 5.2 密码哈希与签名令牌 | `hash_password` / `verify_password` / 令牌，6 项 |
| 5.3 FastAPI 实战与分层 | 无判题，需本机安装 FastAPI 完成自查 |
| 5.4 综合：四端点的迷你 API | `handle_request`，8 项 |

阶段 5 的判题不依赖 FastAPI：路由、校验、PBKDF2 哈希与 HMAC 令牌全部用标准库实现并验证。5.3 给出可运行的真实 FastAPI 应用与分层建议，你在本机 `pip install fastapi uvicorn` 后按自查清单验证。

**阶段 6 · 部署运维**（5 节课，全部为阅读 + 自查清单）

| 课程 | 重点 |
|---|---|
| 6.0 从本机到服务器：部署模型 | 四层架构、12-Factor、三种部署形态 |
| 6.1 Docker：把环境打进镜像 | 多阶段构建、非 root、健康检查、层缓存 |
| 6.2 Compose：一键启动多服务 | api + db + nginx、健康依赖、卷与备份 |
| 6.3 Nginx、HTTPS 与故障排查 | 反向代理头、Certbot、防火墙、502/504 排查 |
| 6.4 上线自查清单与冒烟测试 | 8 组共 40+ 项可验证清单 |

阶段 6 不做判题：Docker、TLS、防火墙这些东西在单文件沙箱里模拟不出真实行为，强行自动化只会制造「通过了但没部署」的假象。每节课末尾都有自查项，6.4 是完整的上线清单。

**阶段 7 · 语言深度**（5 节课 / 4 组练习 / 27 个测试用例）

| 课程 | 练习 |
|---|---|
| 7.0 描述符：属性访问的底层 | `Positive` 描述符，6 项 |
| 7.1 元类：控制类的创建 | `PluginMeta` 自动注册，6 项 |
| 7.2 内存与弱引用 | `__slots__` + `WeakCache`，6 项 |
| 7.3 性能剖析：先测量再优化 | 无判题，本机用 cProfile / tracemalloc 自查 |
| 7.4 综合：迷你 ORM | `Field` + `ModelMeta` + `Model`，9 项 |

七个阶段全部开放。

## 目录结构

```
python-learn/
├── server.py              # HTTP 服务、代码执行、练习判定、进度读写
├── markdown_render.py     # 极简 Markdown → HTML
├── curriculum.json        # 阶段与课时元数据
├── selftest.py            # 开发者自检：用参考答案跑通全部练习
├── content/               # 课程正文（Markdown）
├── exercises/
│   ├── _harness.py        # 测试运行器
│   ├── _mock_service.py   # 阶段 4 的本地异步模拟服务
│   └── 1.1/ … 5.4/        # 每组：starter.py + tests.py + solution.py
├── static/                # 前端（原生 HTML/CSS/JS，无框架）
└── data/progress.json     # 学习进度（运行时生成，已 gitignore）
```

## 加一节课

1. 在 `content/` 写 Markdown（支持标题、列表、表格、代码块、引用、粗体、行内代码）
2. 在 `curriculum.json` 的对应阶段 `lessons` 里加一条记录
3. 如果是编程题，在 `exercises/<id>/` 放 `starter.py` 与 `tests.py`
4. 运行 `python3 selftest.py`，确认测试本身没问题

`tests.py` 的写法：

```python
import solution
from _harness import run


def test_something():
    assert solution.foo(1) == 2, "失败时显示的提示"


run([("用例名称", test_something)])
```

## 执行模型与边界

- 每份代码写入独立临时目录，执行完即删除
- 运行超时 5 秒、检查超时 10 秒，超时强制终止
- 输出超过 20000 字符截断
- 服务只绑定 `127.0.0.1`，仅本机可访问
- 这是学习工具，会执行你写的代码，**不要暴露到公网**

## 自检

```bash
python3 selftest.py
```

会用内置参考答案跑全部练习，并校验课程文件完整性与 Markdown 渲染。

## 与 python-reboot 的关系

`python-reboot/` 是课程资料与项目脚手架：环境清单、任务书、可运行的记账 CLI 参考实现。
`python-learn/` 是交互式学习与验证平台。两者内容对应，练习卡住时可去读参考实现，但先自己写。
