# ErisPulse-Scaffold 脚手架

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://www.python.org/)
[![ErisPulse 2.1.6+](https://img.shields.io/badge/ErisPulse-2.1.6%2B-orange)](https://erispulse.dev)

ErisPulse生态系统的项目脚手架生成工具，快速创建标准化的模块/CLI/适配器项目结构。

## 快速开始

### 作为ErisPulse插件使用

```bash
# 安装脚手架工具
pip install ErisPulse-Scaffold

# 通过epsdk调用
epsdk scaffold
```

## 使用示例

![](.github/assets/use.gif)


## 项目结构

不同模板生成的标准结构：

### 模块模板
```text
module_name/
├── pyproject.toml
├── README.md
├── LICENSE
└── module_name/
    ├── __init__.py
    └── Core.py
```

### CLI模板
```text
cli_name/
├── pyproject.toml
├── README.md
├── LICENSE
└── cli_name/
    ├── __init__.py
    └── cli.py
```

### 适配器模板
```text
adapter_name/
├── pyproject.toml
├── README.md
├── LICENSE
└── adapter_name/
    ├── __init__.py
    ├── Core.py
    └── Converter.py
```

