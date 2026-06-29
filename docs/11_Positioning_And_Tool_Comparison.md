# CodeInsight 定位与工具对比

本文档回答一个关键问题：

> GitHub、CodeQL、Copilot、Continue 等工具已经能做很多代码检查，为什么还要做 CodeInsight？

结论：

CodeInsight 不应该做成低配版 GitHub Actions、CodeQL 或 Continue。它的价值应该放在：

- 项目私有规则
- PR 上下文构建
- Agent / LLM 项目专项审查
- 结构化 Review 输出
- 可评测、可追踪、可编排的自动审查流程

## 1. GitHub 生态已经能做什么

### 1.1 GitHub Actions

GitHub Actions 适合做 CI/CD 自动化，例如：

- 跑测试
- 跑 lint
- 跑类型检查
- 构建 Docker 镜像
- 部署服务
- 阻止未通过检查的 PR 合并

它解决的是：

> 代码变更后，自动执行确定的工程流程。

CodeInsight 不应该重复实现 CI/CD 引擎。CodeInsight 应该接入 CI 结果，或者作为 CI 流程中的一个审查步骤。

参考：

- https://docs.github.com/en/actions/about-github-actions/understanding-github-actions

### 1.2 CodeQL / Code Scanning

CodeQL 和 GitHub Code Scanning 适合做安全漏洞和静态分析，例如：

- 注入风险
- 不安全 API 使用
- 数据流问题
- 已知安全模式

它解决的是：

> 用成熟静态分析规则发现通用安全问题。

CodeInsight 不应该尝试从零复刻 CodeQL。更合理的做法是：

- 让 CodeQL 继续做通用安全扫描
- CodeInsight 做项目上下文、业务规则和 LLM 语义审查
- 后续可以把 CodeQL 结果作为输入上下文之一

参考：

- https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql

### 1.3 Secret Scanning

GitHub Secret Scanning 适合发现提交中的密钥泄露，例如：

- token
- API key
- cloud credential
- private key

它解决的是：

> 发现代码或提交历史中的已知密钥格式。

CodeInsight 当前 MVP 里的 `SEC001` 规则只是为了证明规则引擎和结构化输出闭环，并不是为了长期替代 GitHub Secret Scanning。

长期方向应该是：

- 保留简单规则作为本地解释样例
- 重点做 GitHub 不知道的项目私有安全规则
- 例如“禁止在 agent tool 中暴露未经审计的 shell command”

参考：

- https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning

### 1.4 Dependabot

Dependabot 适合做依赖安全提醒和版本更新，例如：

- 依赖漏洞告警
- 自动创建依赖升级 PR
- 检查 package manifest

它解决的是：

> 第三方依赖是否存在已知漏洞或需要升级。

CodeInsight 不应该重复做依赖漏洞数据库。更合理的是在 PR review 时读取 Dependabot 或 CI 的结果，把它们汇总成更完整的 Review 结论。

参考：

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts

### 1.5 GitHub Copilot Code Review

GitHub Copilot Code Review 可以在 GitHub PR 中提供 AI 辅助审查建议。

它解决的是：

> 在 GitHub 工作流中提供通用 AI review 体验。

CodeInsight 和 Copilot Code Review 的差异不应该是“谁也能说几句 review 建议”，而应该是：

- CodeInsight 的规则可以项目私有化
- CodeInsight 的上下文构建策略可控
- CodeInsight 的输出 schema 可控
- CodeInsight 可以做评测和指标
- CodeInsight 可以专门针对 Agent / LLM 应用做审查
- CodeInsight 可以把审查过程拆成可解释 pipeline

参考：

- https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review

## 2. Continue 已经能做什么

Continue 更像是开发者本地 IDE 内的 AI 编程助手。它适合：

- 在 VS Code / JetBrains 中聊天式理解代码
- 根据当前文件或代码库上下文生成代码
- 辅助补全
- 辅助修改代码
- 接入不同模型
- 在开发者本地工作流里提高编码效率

它解决的是：

> 开发者写代码时，如何在 IDE 中更快理解、生成和修改代码。

CodeInsight 不应该做成本地聊天助手。CodeInsight 的定位应该是：

> PR 发生之后，自动执行可追踪、可评测、可结构化输出的审查流程。

Continue 偏“开发中”。

CodeInsight 偏“PR 审查中”。

参考：

- https://docs.continue.dev/

## 3. 对比总览

| 工具 | 主要场景 | 擅长什么 | CodeInsight 不该重复什么 | CodeInsight 应该补什么 |
| --- | --- | --- | --- | --- |
| GitHub Actions | CI/CD | 自动跑测试、lint、构建、部署 | 不重复做 CI 引擎 | 作为 CI 中的智能 review step |
| CodeQL | 安全静态分析 | 通用漏洞模式、数据流分析 | 不复刻静态分析规则库 | 结合项目上下文解释风险 |
| Secret Scanning | 密钥扫描 | 已知 token / key 格式检测 | 不做低配密钥扫描器 | 做项目私有安全规则 |
| Dependabot | 依赖安全 | 漏洞告警、依赖升级 PR | 不维护漏洞数据库 | 汇总依赖风险到 review 报告 |
| Copilot Code Review | GitHub PR AI review | 通用 AI 审查建议 | 不只做通用建议生成 | 做可控 schema、私有规则、评测 |
| Continue | IDE AI 助手 | 本地编码、问答、补全、修改 | 不做 IDE 聊天助手 | 做 PR 后自动审查 pipeline |
| CodeInsight | PR 自动审查服务 | 项目规则、上下文、LLM reasoning、结构化报告 | 不重复成熟平台基础能力 | 做定制化、可解释、可评测审查 |

## 4. CodeInsight 的差异化方向

### 4.1 项目私有规则

通用工具不知道项目内部约束。

CodeInsight 应该支持这类规则：

```text
API 层不能直接访问数据库
core/reasoning 不能调用 github 模块
prompt 文件必须包含版本号
LLM 输出必须有 JSON schema 校验
tool calling 必须有 timeout 和 retry
新增 agent tool 必须有权限边界说明
evaluation metric 不能在普通 feature PR 中被修改
```

这些规则更接近真实团队的工程规范，而不是通用 lint。

### 4.2 PR 上下文构建

普通 diff 只告诉你改了什么，不告诉你影响了什么。

CodeInsight 后续应该构建：

```text
本次 diff
变更文件列表
相关函数
调用方
被调用方
项目目录角色
历史规则
测试覆盖情况
```

这样 LLM reviewer 才不是只看几行代码，而是带着上下文做判断。

### 4.3 Agent / LLM 项目专项审查

这是 CodeInsight 最适合作为简历项目的方向。

它可以检查：

```text
是否把业务规则硬编码在 prompt 里
是否缺少 structured output schema
是否缺少 LLM 调用超时
是否缺少重试和降级策略
是否没有记录 tool call trace
是否把 retrieval 和 reasoning 混在一起
是否没有 hallucination guardrail
是否没有 evaluation dataset
是否没有 prompt versioning
是否没有 cost / latency 记录
```

这些问题 GitHub Actions 和传统静态分析通常不会直接覆盖。

### 4.4 结构化输出

CodeInsight 的输出不应该只是自然语言。

目标输出应该是：

```json
{
  "severity": "high",
  "file": "core/review/service.py",
  "line": 42,
  "rule_id": "ARCH001",
  "reason": "API layer bypasses review service abstraction.",
  "suggestion": "Move GitHub-specific logic into core/github.",
  "confidence": 0.82,
  "source": "policy+context+llm"
}
```

结构化输出的价值：

- 可以自动评论到 PR
- 可以做统计
- 可以做评测
- 可以做误报分析
- 可以区分规则发现和 LLM 推理发现

### 4.5 可评测

很多 AI code review 工具的问题是：

> 看起来能说，但不知道说得准不准。

CodeInsight 应该从早期就建立 evaluation：

```text
输入：历史 diff 或人工构造 diff
期望输出：应该发现的问题
指标：命中率、误报率、漏报率、平均延迟、LLM 成本
```

这会让项目更像工程系统，而不是 prompt demo。

## 5. 当前 MVP 规则的真实意义

当前 MVP 已有规则：

```text
SEC001: hardcoded secret
DBG001: debug print
MTN001: TODO / FIXME
```

这些规则本身不高级，GitHub 生态也有大量工具能覆盖类似问题。

它们的意义是验证闭环：

```text
输入 diff
解析新增行
执行规则
生成 finding
输出 JSON
API 返回结果
测试覆盖
CI 自动运行
```

所以当前阶段不是在证明“我比 GitHub 扫描更强”，而是在证明：

> 我已经搭好了一个可扩展的 PR review pipeline。

## 6. 后续路线调整建议

为了避免项目变成低配版 GitHub 工具，后续路线应该调整成：

### Day 4-7

- 提取 diff 涉及文件列表
- 建立仓库文件结构 parser
- 标记文件所属层级，例如 API / core / test / config
- 把 diff fetcher 和 review pipeline 串起来

### Week 2

- 做上下文构建，而不是急着堆向量库
- 先基于文件路径、导入关系、函数名做 symbol retrieval
- 后续再考虑 Qdrant

### Week 3

- 做 Agent / LLM 项目专项 reviewer
- 检查 schema、timeout、retry、prompt version、tool boundary、evaluation

### Week 4

- GitHub PR comment integration
- evaluation dataset
- latency / cost / false positive 记录
- Docker Compose 和部署文档

## 7. 面试表达

可以这样讲：

> 我没有把 CodeInsight 做成 GitHub Actions 或 CodeQL 的替代品。GitHub 生态已经能很好地完成 CI、依赖扫描、密钥扫描和通用安全分析。CodeInsight 的定位是补足这些工具不擅长的部分：项目私有规则、PR 上下文构建、Agent/LLM 项目专项审查，以及可评测的结构化 Review 输出。

更短版本：

> CodeInsight 不是重复造一个低配 GitHub 工具，而是做一个面向 Agent/LLM 项目的定制化 PR reviewer。

