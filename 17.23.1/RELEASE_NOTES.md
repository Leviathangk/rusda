## Rusda 17.23.1

基于官方 Frida 17.23.1（`e4767b7e9af033f8b2b1fe02f1808228615d93f1`）移植 rusda 补丁，使用 Android NDK r29 构建。

- 提供 Android `arm`、`arm64`、`x86`、`x86_64` 的 `server`、`inject`、`gadget`，共 12 个 `.xz` 文件。
- 延续进程/产物改名、线程与 RPC 字符串处理，以及链接后的 ELF 特征字符串处理。
- 移除两处已不适用于上游新版的旧补丁：`droidy-client.vala` 已删除，Android helper 的 `--nice-name` 启动路径已重构。
- `SHA256SUMS` 列出所有发布产物的校验值。

构建与二进制静态检查已通过；本次没有连接的 Android 设备，未进行真机注入测试。

源码补丁和复现步骤见 `17.23.1/patches/deliver/README.txt`。
