import argparse
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Callable
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.tree import Tree
from rich.text import Text

# 类型别名定义
ProjectInfo = Dict[str, str]
ScaffoldCreator = Callable[[Path, ProjectInfo], None]

class ScaffoldGenerator:
    """脚手架生成器基类"""
    
    @staticmethod
    def register_command(subparsers: Any, console: Console) -> None:
        """注册脚手架生成命令"""
        parser = subparsers.add_parser(
            'scaffold',
            help='生成ErisPulse项目脚手架 (模块/CLI/适配器)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=".",
            help='输出目录 (默认为当前目录)'
        )
        parser.set_defaults(func=lambda args: ScaffoldGenerator.handle_scaffold(args, console))
    
    @staticmethod
    def handle_scaffold(args: argparse.Namespace, console: Console) -> None:
        """处理脚手架生成命令"""
        try:
            console.print(Panel("ErisPulse 脚手架生成器", style="blue"))
            
            project_info = ScaffoldGenerator._collect_project_info(console)
            if not project_info:
                console.print("已取消", style="yellow")
                return
            
            ScaffoldGenerator._create_project_structure(args.output, project_info, console)
            
        except Exception as e:
            console.print(Panel(f"错误: {e}", style="error"))
            raise
    
    @staticmethod
    def _collect_project_info(console: Console) -> ProjectInfo:
        """收集项目信息"""
        project_type = Prompt.ask(
            "请选择要创建的项目类型",
            choices=["module", "cli", "adapter"],
            default="module"
        )
        
        name = Prompt.ask("请输入项目名称", default=f"ErisPulse-{project_type.capitalize()}")
        version = Prompt.ask("请输入版本号", default="1.0.0")
        description = Prompt.ask("请输入项目描述", default="一个非常哇塞的ErisPulse项目")
        author_name = Prompt.ask("请输入作者姓名", default="yourname")
        author_email = Prompt.ask("请输入作者邮箱", default="your@mail.com")
        homepage = Prompt.ask("请输入项目主页URL", default=f"https://github.com/{author_name}/{name}")

        info = {
            'type': project_type,
            'name': name,
            'version': version,
            'description': description,
            'author_name': author_name,
            'author_email': author_email,
            'homepage': homepage
        }
        
        console.print("\n[bold]项目信息:[/bold]")
        for key, value in info.items():
            console.print(f"{key}: {value}")
            
        if not Confirm.ask("\n确认创建项目吗?"):
            return {}
            
        return info
    
    @staticmethod
    def _create_project_structure(output_dir: str, project_info: ProjectInfo, console: Console) -> None:
        """创建项目结构"""
        base_dir = Path(output_dir) / project_info['name']
        base_dir.mkdir(parents=True, exist_ok=True)
        
        creators = {
            'module': ModuleCreator,
            'cli': CLICreator,
            'adapter': AdapterCreator
        }
        
        creator = creators[project_info['type']]()
        creator.create(base_dir, project_info)
        
        ScaffoldGenerator._display_result(base_dir, project_info['name'], console)
    
    @staticmethod
    def _display_result(base_dir: Path, name: str, console: Console) -> None:
        """显示生成结果"""
        tree = Tree(f"[green]{name}[/green]")
        ScaffoldGenerator._add_directory_to_tree(base_dir, tree)
        console.print(Panel(tree, title="生成的项目结构"))
        
        console.print(Panel(
            f"项目已成功创建在 {base_dir}\n"
            "接下来您可以:\n"
            "1. 进入目录并开始开发\n"
            f"2. 运行 'pip install -e ./{base_dir}' 进行开发模式安装\n"
            "3. 运行 'ep-init' 初始化本目录为ep项目\n"
            "3. 使用 'epsdk run main.py' 测试您的模块",
            style="success"
        ))
    
    @staticmethod
    def _add_directory_to_tree(directory: Path, tree: Tree) -> None:
        """将目录结构添加到Rich Tree中"""
        for item in sorted(directory.iterdir()):
            if item.is_dir():
                branch = tree.add(Text(item.name, style="bold blue"))
                ScaffoldGenerator._add_directory_to_tree(item, branch)
            else:
                tree.add(Text(item.name, style="green"))

class ModuleCreator:
    """模块脚手架生成器"""
    
    def create(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建模块脚手架"""
        module_dir = base_dir / project_info['name'].replace("-", "_")
        module_dir.mkdir()
        
        self._create_pyproject(base_dir, project_info)
        self._create_readme(base_dir, project_info)
        self._create_license(base_dir)
        self._create_core_file(module_dir, project_info)
        self._create_init_file(module_dir, project_info)
    
    def _create_pyproject(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建pyproject.toml文件"""
        content = f"""[project]
name = "{project_info['name']}"
version = "{project_info['version']}"
description = "{project_info['description']}"
readme = "README.md"
requires-python = ">=3.9"
license = {{ file = "LICENSE" }}
authors = [ {{ name = "{project_info['author_name']}", email = "{project_info['author_email']}" }} ]

dependencies = [
]

[project.urls]
"homepage" = "{project_info['homepage']}"

[project.entry-points."erispulse.module"]
"{project_info['name'].split('-')[-1]}" = "{project_info['name'].replace('-', '_')}:Main"
"""
        (base_dir / "pyproject.toml").write_text(content, encoding="utf-8")
    
    def _create_readme(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建README.md文件"""
        (base_dir / "README.md").write_text(
            f"# {project_info['name']}\n\n{project_info['description']}", 
            encoding="utf-8"
        )
    
    def _create_license(self, base_dir: Path) -> None:
        """创建LICENSE文件"""
        (base_dir / "LICENSE").write_text("""MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted...""")
    
    def _create_core_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建Core.py文件"""
        module_name = project_info['name'].split('-')[-1]
        content = f"""# 你也可以直接导入对应的模块
# from ErisPulse import sdk
# from ErisPulse.Core import logger, env, raiserr, adapter

class Main:
    def __init__(self, sdk):    # 这里也可以不接受sdk参数
        self.sdk = sdk
        self.env = self.sdk.env
        self.logger = self.sdk.logger
        
        self.logger.info("{module_name} 初始化完成")
        self.config = self._load_config()
    
    # 加载配置方法，你需要在这里进行必要的配置加载逻辑
    def _load_config(self):
        _config = self.env.getConfig("{module_name}", {{}})
        if _config is None:
            default_config = {{
                "key": "value",
                "key2": [1, 2, 3],
                "key3": {{
                    "key4": "value4"
                }}
            }}
            self.env.setConfig("{module_name}", default_config)
            return default_config
        return _config
            
    def hello(self):
        self.logger.info("Hello World!")
        # 其它模块可以通过 sdk.{module_name}.hello() 调用此方法
"""
        (module_dir / "Core.py").write_text(content, encoding="utf-8")
    
    def _create_init_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建__init__.py文件"""
        (module_dir / "__init__.py").write_text("from .Core import Main", encoding="utf-8")

class CLICreator:
    """CLI脚手架生成器"""
    
    def create(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建CLI脚手架"""
        module_dir = base_dir / project_info['name'].replace("-", "_")
        module_dir.mkdir()
        
        self._create_pyproject(base_dir, project_info)
        self._create_readme(base_dir, project_info)
        self._create_license(base_dir)
        self._create_cli_file(module_dir, project_info)
        self._create_init_file(module_dir, project_info)
    
    def _create_pyproject(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建pyproject.toml文件"""
        content = f"""[project]
name = "{project_info['name']}"
version = "{project_info['version']}"
description = "{project_info['description']}"
readme = "README.md"
requires-python = ">=3.9"
license = {{ file = "LICENSE" }}
authors = [ {{ name = "{project_info['author_name']}", email = "{project_info['author_email']}" }} ]

dependencies = [
    "ErisPulse>=2.1.6"
]

[project.urls]
"homepage" = "{project_info['homepage']}"

[project.entry-points."erispulse.cli"]
"{project_info['name'].split('-')[-1].lower()}" = "{project_info['name'].replace('-', '_')}:cli_register"
"""
        (base_dir / "pyproject.toml").write_text(content, encoding="utf-8")
    
    def _create_readme(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建README.md文件"""
        (base_dir / "README.md").write_text(
            f"# {project_info['name']}\n\n{project_info['description']}", 
            encoding="utf-8"
        )
    
    def _create_license(self, base_dir: Path) -> None:
        """创建LICENSE文件"""
        (base_dir / "LICENSE").write_text("""MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted...""", encoding="utf-8")
    
    def _create_cli_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建cli.py文件"""
        command_name = project_info['name'].split('-')[-1].lower()
        content = f"""import argparse
from typing import Any
from rich.panel import Panel
from rich.console import Console

def cli_register(subparsers: Any, console: Console) -> None:
    \"\"\"
    注册自定义CLI命令
    
    参数:
        subparsers: argparse的子命令解析器
        console: 主CLI提供的控制台输出实例
    \"\"\"
    # 创建命令解析器
    parser = subparsers.add_parser(
        '{command_name}',  # 命令名称
        help='{project_info['description']}'
    )
    
    # 添加参数
    parser.add_argument(
        '--option',
        type=str,
        default='default',
        help='选项描述'
    )
    
    # 命令处理函数
    def handle_command(args: argparse.Namespace):
        try:
            console.print(Panel("命令开始执行", style="info"))
            
            # 你的命令逻辑
            console.print(f"执行操作，选项值: {{args.option}}")
            
            console.print(Panel("命令执行完成", style="success"))
        except Exception as e:
            console.print(Panel(f"错误: {{e}}", style="error"))
            raise
    
    # 设置处理函数
    parser.set_defaults(func=handle_command)
"""
        (module_dir / "cli.py").write_text(content, encoding="utf-8")
    
    def _create_init_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建__init__.py文件"""
        (module_dir / "__init__.py").write_text("from .cli import cli_register", encoding="utf-8")

class AdapterCreator:
    """适配器脚手架生成器"""
    
    def create(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建适配器脚手架"""
        module_dir = base_dir / project_info['name'].replace("-", "_")
        module_dir.mkdir()
        
        self._create_pyproject(base_dir, project_info)
        self._create_readme(base_dir, project_info)
        self._create_license(base_dir)
        self._create_core_file(module_dir, project_info)
        self._create_converter_file(module_dir, project_info)
        self._create_init_file(module_dir, project_info)
    
    def _create_pyproject(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建pyproject.toml文件"""
        content = f"""[project]
name = "{project_info['name']}"
version = "{project_info['version']}"
description = "{project_info['description']}"
readme = "README.md"
requires-python = ">=3.9"
license = {{ file = "LICENSE" }}
authors = [ {{ name = "{project_info['author_name']}", email = "{project_info['author_email']}" }} ]

dependencies = [
]

[project.urls]
"homepage" = "{project_info['homepage']}"

[project.entry-points."erispulse.adapter"]
"{project_info['name'].split('-')[-1]}" = "{project_info['name'].replace('-', '_')}:{project_info['name'].split('-')[-1]}"
"""
        (base_dir / "pyproject.toml").write_text(content, encoding="utf-8")
    
    def _create_readme(self, base_dir: Path, project_info: ProjectInfo) -> None:
        """创建README.md文件"""
        (base_dir / "README.md").write_text(
            f"# {project_info['name']}\n\n{project_info['description']}", 
            encoding="utf-8"
        )
    
    def _create_license(self, base_dir: Path) -> None:
        """创建LICENSE文件"""
        (base_dir / "LICENSE").write_text("""MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted...""")
    
    def _create_core_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建Core.py文件"""
        adapter_name = project_info['name'].split('-')[-1]
        content = f"""import asyncio
from typing import Optional
from ErisPulse.Core import BaseAdapter
# 你也可以直接导入对应的模块
# from ErisPulse import sdk
# from ErisPulse.Core import logger, env, raiserr, adapter

class {adapter_name}(BaseAdapter):
    def __init__(self, sdk):    # 这里也可以不接受sdk参数
        self.sdk = sdk
        self.env = self.sdk.env
        self.logger = self.sdk.logger
        
        self.logger.info("{adapter_name} 初始化完成")
        self.config = self._load_config()
    
    # 加载配置方法，你需要在这里进行必要的配置加载逻辑
    def _load_config(self):
        _config = self.env.getConfig("{adapter_name}", {{}})
        if _config is None:
            default_config = {{
                "mode": "server",
                "server": {{
                    "path": "/webhook",
                }},
                "client": {{
                    "url": "http://127.0.0.1:8080",
                    "token": ""
                }}
            }}
            self.env.setConfig("{adapter_name}", default_config)
            return default_config
        return _config
    
    class Send(BaseAdapter.Send):
        def Text(self, text: str):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="/send",
                    content=text,
                    recvId=self._target_id,
                    recvType=self._target_type
                )
            )
            
        def Image(self, file: bytes):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="/send_image",
                    file=file,
                    recvId=self._target_id,
                    recvType=self._target_type
                )
            )

    async def call_api(self, endpoint: str, **params):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()
        
    async def shutdown(self):
        raise NotImplementedError()
"""
        (module_dir / "Core.py").write_text(content, encoding="utf-8")
    
    def _create_converter_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建Converter.py文件"""
        adapter_name = project_info['name'].split('-')[-1].lower()
        content = f"""import time
from typing import Optional

class {project_info['name'].split('-')[-1]}Converter:
    def convert(self, raw_event: dict) -> Optional[dict]:
        \"\"\"将平台原生事件转换为OneBot12标准格式\"\"\"
        if not isinstance(raw_event, dict):
            return None

        # 基础事件结构
        onebot_event = {{
            "id": str(raw_event.get("event_id", "generated_id")),
            "time": int(time.time()),
            "type": "",  # message/notice/request/meta_event
            "detail_type": "",
            "platform": "{adapter_name}",
            "self": {{
                "platform": "{adapter_name}",
                "user_id": str(raw_event.get("bot_id", ""))
            }},
            "{adapter_name}_raw": raw_event  # 保留原始数据
        }}

        # 根据事件类型分发处理
        event_type = raw_event.get("type")
        if event_type == "message":
            return self._handle_message(raw_event, onebot_event)
        elif event_type == "notice":
            return self._handle_notice(raw_event, onebot_event)
        
        return None

    def _handle_message(self, raw_event: dict, onebot_event: dict) -> dict:
        \"\"\"处理消息事件\"\"\"
        onebot_event["type"] = "message"
        # 添加你的消息处理逻辑
        return onebot_event

    def _handle_notice(self, raw_event: dict, onebot_event: dict) -> dict:
        \"\"\"处理通知事件\"\"\"
        onebot_event["type"] = "notice"
        # 添加你的通知处理逻辑
        return onebot_event
"""
        (module_dir / "Converter.py").write_text(content, encoding="utf-8")
    
    def _create_init_file(self, module_dir: Path, project_info: ProjectInfo) -> None:
        """创建__init__.py文件"""
        adapter_name = project_info['name'].split('-')[-1]
        (module_dir / "__init__.py").write_text(f"from .Core import {adapter_name}", encoding='utf-8')

def scaffold_register(subparsers: Any, console: Console) -> None:
    """脚手架生成命令注册入口"""
    ScaffoldGenerator.register_command(subparsers, console)