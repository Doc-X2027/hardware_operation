# 本地 Aravis 运行库

本机已通过 Ubuntu 22.04 软件源下载并解包 `gir1.2-aravis-0.8`、`libaravis-0.8-0`（0.8.20-1，amd64）。`usr/` 内含动态库、GI typelib 及发行版版权文件，版权信息见 `usr/share/doc/*/copyright`。不包含 Windows DLL 或海康专有 SDK。

二进制及 deb 包由本目录的上级 `.gitignore` 排除，不提交 Git。其他电脑可运行 `../install_local.sh` 重新下载，或按主 README 安装系统包。下载版本由该电脑的软件源决定。

`run.sh` 为当前进程设置库搜索路径；不写入系统目录，也不修改全局环境。本地包适用于 Ubuntu 22.04 x86_64，其他发行版或架构优先使用自身的系统包。
