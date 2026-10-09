## Rusda 17.23.1 iOS（实验性）

基于官方 Frida 17.23.1，在 rusda 同版本补丁上增加 iOS Mach-O 处理和 agent 入口点改名。由 macOS 15.6.1、Xcode 26.3 在 Apple Silicon Mac 上构建。

- `rusda-server-17.23.1-ios-arm64.xz`：arm64
- `rusda-inject-17.23.1-ios-arm64.xz`：arm64
- `rusda-gadget-17.23.1-ios-universal.dylib.xz`：arm64 + arm64e
- `SHA256SUMS`：以上三个文件的 SHA-256 校验值

所有产物均使用 ad-hoc 签名。构建产物及 arm64、arm64e agent 通过 Mach-O 架构、签名和适用的关键指纹静态检查，压缩包通过 `xz -t` 和 SHA-256 检查。尚未完成 iOS 真机运行与注入测试；这次也没有发布 Apple Development 证书签名的版本。

复现步骤、补丁和已知边界见仓库的 `17.23.1/ios/README.md`。
