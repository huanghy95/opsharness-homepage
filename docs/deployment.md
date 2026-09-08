# OpsHarness 公网发布说明

## 当前进度（2026-09-08）

- 仓库：https://github.com/huanghy95/opsharness-homepage
- 主页代码已上传至远端 `main` 分支，仓库保持 Private。
- GitHub Pages 尚未启用：GitHub API 返回 `Your current plan does not support GitHub Pages for this repository.`
- 需要选择将仓库改为 Public，或保留 Private 并升级至支持私有仓库 Pages 的套餐（个人账号为 GitHub Pro）。
- `opsharness.ai` 尚未购买，尚未配置自定义域名。

GitHub Pages 的私有仓库套餐要求见[官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

## 先启用 GitHub Pages

在解决上述套餐限制后，打开[仓库 Pages 设置](https://github.com/huanghy95/opsharness-homepage/settings/pages)：

1. Source 选择 `Deploy from a branch`。
2. Branch 选择 `main`，目录选择 `/ (root)`，保存。
3. 等待仓库 Actions 中的 Pages 部署成功。
4. 验证 https://huanghy95.github.io/opsharness-homepage/ 可以访问。

该地址目前只是预期发布地址，尚未上线。仓库中的 `_config.yml` 会将 README、开发文档和测试排除在发布内容之外。

## 购买 opsharness.ai

可以在 [Porkbun 的 .ai 注册页面](https://porkbun.com/tld/ai)搜索 `opsharness.ai`：

1. 注册自己的账号并验证邮箱。
2. 输入完整域名，确认是否可注册，以及是否为普通定价域名。
3. 选择至少两年的注册期，核对订单总价及续费价格。
4. 填写真实注册人资料，由域名持有人完成付款。
5. 完成注册商要求的邮箱验证，并根据需要开启自动续费。

截至本次查询，Porkbun 的普通 `.ai` 域名公开标价为注册和续费均 $82.70/年，最低注册和续费期限为两年，因此按此单价计算的两年费用约 $165.40。具体域名是否可注册、是否为溢价域名、税费和最终价格均以搜索及结账页面为准；本次未确认 `opsharness.ai` 的可注册状态。

依据：[.ai 价格与最低期限](https://porkbun.com/tld/ai)、[价格口径（按年，非溢价域名）](https://porkbun.com/products/domains/)。

此次购买只需要域名，主页托管由 GitHub Pages 提供。

## 购买后绑定域名

先完成 GitHub Pages 的发布，再进行以下操作：

1. 在仓库 **Settings → Pages → Custom domain** 中保存 `opsharness.ai`，不填写 `https://`。
2. 在注册商的 DNS 管理界面为该域名添加：

| 类型 | 主机记录 | 值 |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | huanghy95.github.io |

3. 等待 GitHub 的 DNS 检查通过和 HTTPS 证书就绪，勾选 **Enforce HTTPS**。DNS 生效及该选项可用可能需要最多 24 小时。
4. 访问 https://opsharness.ai 并检查图片、语言切换和结果表。

依据：[GitHub 自定义域名设置](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)。

GitHub 保存自定义域名时会在远端添加 `CNAME` 文件。下次本地更新前，先在主页工作树执行 `git pull --ff-only origin main`，将该提交同步到本地。
