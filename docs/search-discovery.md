# 搜索收录与曝光维护

主页：<https://opsharness.org/>。本次配置日期：2026-09-09。

## 为什么刚发布时搜不到

本次 Google Search Console 的首页检查显示“网址尚未收录到 Google”，
具体原因为“Google 无法识别此网址”，没有历史抓取时间。这是新站尚未被
发现的状态，不是已经确认的处罚或抓取错误。公开首页返回 HTTP 200，
没有 `noindex` 或禁止抓取的设置。

Google 搜到 arXiv 论文或第三方介绍，并不代表已经收录了新的项目域名。
“验证所有权”“提交站点地图”“请求索引”“实际收录”和“搜索排名”是不同阶段。

## 已完成的站内配置

- 搜索标题加入品牌名：`OpsHarness | Self-Evolving Harness for Root Cause Analysis`。
- 补齐页面描述、分享标题、站点名称和图片说明；保留正式论文标题与 BibTeX。
- canonical 指向唯一主页 `https://opsharness.org/`。
- 添加 `WebSite`、`WebPage`、`ScholarlyArticle` JSON-LD 和论文引用元数据。
- 发布 [robots.txt](https://opsharness.org/robots.txt)，允许搜索引擎抓取并声明站点地图。
- 发布 [sitemap.xml](https://opsharness.org/sitemap.xml)，仅列出实际存在的主页。
- 为 GitHub 仓库增加主页链接、项目描述和相关 topics。

这些配置帮助搜索引擎理解网站，不保证排名、富媒体结果或 Google Scholar 收录。
原本缺少 robots.txt / sitemap.xml 本身不等于禁止收录。

## Google Search Console

[打开 opsharness.org 资源](https://search.google.com/search-console?resource_id=sc-domain%3Aopsharness.org)。
使用本次操作所用的 Google 账号登录。

- Domain property：`opsharness.org`，覆盖该域名的协议和子域名。
- 所有权：已通过 Porkbun DNS TXT 验证。请保留根域名下的
  `google-site-verification=…` TXT 记录，也保留已有的 GitHub 验证 TXT。
- 站点地图：`https://opsharness.org/sitemap.xml` 已提交，状态“成功”，
  2026-09-09 已发现 1 个网页。
- 首页实时测试：2026-09-09 通过，Google 显示“网址可编入 Google 索引”。
- 首页索引请求：已受理，Google 显示“已请求编入索引”，并确认已加入优先抓取队列。
  这不是已经收录的确认；本次操作结束时，正式索引仍需等待 Google 处理。

复查时，在 Search Console 顶部输入 `https://opsharness.org/`，查看网址检查结果。
若还未收录，先检查“网页索引编制”中的具体原因；不要将新资源的“数据处理中”
误当作网站异常，也不要反复请求索引。收录后，在“效果”中查看 `opsharness`
搜索词的展示次数、点击量与平均排名。

Google 表示重新抓取可能需要几天到几周，请求并不保证收录或立刻显示。
正式索引状态以 Search Console 为准，`site:opsharness.org` 搜索仅供辅助检查。

## 后续最值得做的曝光工作（尚未代为执行）

1. 在 arXiv 的项目链接/Comments 等合适位置加入主页地址，按 arXiv 的更新规则操作。
2. 在作者个人主页、实验室论文列表和正式开源仓库中加入可点击的项目主页链接。
3. 发布项目介绍时统一使用 `OpsHarness` 品牌名和 `https://opsharness.org/`。
   重点说明方法、结果和实际用途，避免购买外链、刷流量或堆砌关键词。
4. 按需在 Bing Webmaster Tools 中验证同一域名并提交站点地图；
   本次没有连接 Bing/百度账号或向这些平台提交。

## 以后修改网站时

- 继续保留 `CNAME`、canonical、robots.txt、sitemap.xml 及两条 DNS 验证 TXT。
- 页面发生实质内容更新时再更新 sitemap 的 `lastmod`，不要每日自动改日期。
- 新增独立页面时，把实际、可索引的规范 URL 加入 sitemap。不要加入 `#method`
  等页内锚点，也不要给同页中英文切换捏造独立 URL 或 hreflang。
- 当前默认英语正文可在不运行 JavaScript 时读取。若以后需要独立中文搜索落地页，
  应另建真实的中文 URL，再配置对应语言关系。
- 发布前执行 `python3 -m unittest discover -s tests -v`，上线后检查三个公开 URL
  （首页、robots.txt、sitemap.xml）均正常返回，且内容与仓库一致。

参考：[Google 请求重新抓取](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)、
[站点地图指南](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)、
[网站名称结构化数据](https://developers.google.com/search/docs/appearance/site-names)。
