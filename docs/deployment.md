# OpsHarness 公网发布说明

## 当前配置（2026-09-09）

- 仓库：https://github.com/huanghy95/opsharness-homepage
- 已按用户授权将主页仓库改为 Public。
- GitHub Pages 已启用，发布源为 `main` 分支的 `/ (root)`。
- 正式域名：`opsharness.org`，由用户在 Porkbun 注册。
- 目标地址：https://opsharness.org/
- 原地址：https://huanghy95.github.io/opsharness-homepage/ ，GitHub 会自动重定向至自定义域名。
- `www.opsharness.org` 指向同一网站，并由 GitHub 重定向至根域名。
- 每次推送到远端 `main` 分支都会触发部署，可在仓库 Actions 中查看结果。
- GitHub 账户的域名所有权验证已通过，仓库 Pages 显示 `DNS check successful`。
- HTTPS：正在等待 GitHub 自动签发证书；证书就绪后开启 `Enforce HTTPS`。

GitHub Pages 的私有仓库套餐要求见[官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

## 当前 GitHub Pages 配置

打开[仓库 Pages 设置](https://github.com/huanghy95/opsharness-homepage/settings/pages)可查看或恢复配置：

1. Source 选择 `Deploy from a branch`。
2. Branch 选择 `main`，目录选择 `/ (root)`，保存。
3. 等待仓库 Actions 中的 Pages 部署成功。
4. Custom domain 为 `opsharness.org`，不包含协议或路径。
5. DNS 检查成功后，等待证书签发，勾选 `Enforce HTTPS`。

仓库中的 `_config.yml` 会将 README、开发文档和测试排除在发布内容之外；它们仍可在公开的源码仓库中查看。

## Porkbun DNS 配置

继续使用 Porkbun 原有 Nameservers，没有购买或切换托管服务。记录 TTL 均为 600 秒：

| 类型 | 主机记录 | 值 |
| --- | --- | --- |
| ALIAS | 留空（根域名） | huanghy95.github.io |
| CNAME | www | huanghy95.github.io |
| TXT | _github-pages-challenge-huanghy95 | 保留 GitHub 账户验证页提供的验证码 |

根域名 ALIAS 会自动解析为 GitHub Pages 的 IP 地址，无需再叠加手工 A 记录。
验证时公共 DNS 返回 `185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153`。

原有根域名停放 ALIAS 已改为 GitHub 目标；原有 `*` 停放 CNAME 已改为 `www`，不保留通配符。
请勿删除 TXT 验证记录，它用于保护域名，防止被其他 GitHub 用户用于 Pages。

## HTTPS 与验收

DNS 传播及 HTTPS 选项可用可能需要最多 24 小时。证书尚未就绪时不要绕过浏览器警告，也不需要另购 SSL。
若长时间未就绪，先检查上述 DNS 记录及域名状态，再查阅官方排障文档。

- https://opsharness.org/ 正常打开且无证书警告。
- http://opsharness.org/ 自动跳转到 HTTPS。
- https://www.opsharness.org/ 和原 GitHub 地址跳转到正式地址。
- 图片、样式、语言切换和完整结果表正常。
- 新发布的 HTML 与本地提交保持一致。

依据：[GitHub 自定义域名设置](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)。

## 后续更新

在主页工作树执行 `git pull --ff-only origin main` 后修改，验证并提交，再执行 `git push origin HEAD:main`。
务必保留根目录 `CNAME` 文件，内容为 `opsharness.org`；GitHub 自动创建的该文件已同步到本地。
网页 canonical、Open Graph URL 和分享图片地址也使用该域名。

域名验证参考：[GitHub 官方说明](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)。
