# Rusda 17.23.1 iOS 构建

基线是官方 Frida 17.23.1。当前产物由 macOS 15.6.1、Xcode 26.3 在 Apple Silicon Mac 上构建，使用临时（ad-hoc）签名：

- `rusda-server-17.23.1-ios-arm64.xz`
- `rusda-inject-17.23.1-ios-arm64.xz`
- `rusda-gadget-17.23.1-ios-universal.dylib.xz`（arm64 + arm64e）

## 复现

在 macOS 上准备 Xcode、Command Line Tools、Homebrew Node.js 和 Python 3，然后执行：

```bash
git clone --recurse-submodules -b 17.23.1 https://github.com/frida/frida.git frida17.23.1-ios
cd frida17.23.1-ios
RUSDA=/path/to/rusda/17.23.1

git apply --exclude=releng "$RUSDA/patches/deliver/superrepo.patch"
( cd subprojects/frida-core && git apply "$RUSDA/patches/deliver/frida-core.patch" )
( cd subprojects/frida-gum && git apply "$RUSDA/patches/deliver/frida-gum.patch" )
( cd subprojects/frida-core && git apply "$RUSDA/ios/frida-core-ios.patch" )

export PATH="/opt/homebrew/bin:$PATH"
export PYTHON=/opt/homebrew/bin/python3
export IOS_CERTID=-
mkdir build-ios-arm64
cd build-ios-arm64
../configure --prefix="$PWD/../dist-ios" --host=ios-arm64 \
  --enable-server --enable-gadget --enable-inject
make -j4
make install
cd ..
python3 "$RUSDA/ios/verify-ios.py" "$PWD"
```

`frida-core-ios.patch` 叠加在同版本的 Android 通用补丁之后，增加 iOS agent 入口点处理，以及在签名前对 Mach-O 字符串、符号做等长替换。`topatch-macho.py` 是补丁内新增文件的独立副本，方便查看。

三个发布文件均通过 `xz -t`、SHA-256、`codesign --verify` 和 `lipo -info` 检查；构建树中的 arm64、arm64e agent 也通过了签名及关键字符串检查。当前没有完成 iOS 真机运行、注入或 App 兼容性测试，不能据此断言运行时可用性或所有 Frida 指纹都已清除。

本次发布使用 ad-hoc 签名。若要放入普通 iOS App，需要按目标 App 的签名与安装流程重新签名；`rusda-server` 的运行环境也取决于设备权限。通过 SSH 使用现有 Apple Development 证书签名时，Mac 钥匙串返回 `errSecInternalComponent`，所以没有将开发者证书签名的产物发布。
