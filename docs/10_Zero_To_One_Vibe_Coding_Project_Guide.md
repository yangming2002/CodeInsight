# CodeInsight 从 0 到 1 开发指南

本文档面向 0 项目、0 实习经验的新手，目标是把 CodeInsight 从一个文档骨架推进成一个能运行、能测试、能部署、能写进简历的工程项目。

## 1. 项目定位

CodeInsight 是一个面向 GitHub Pull Request 的智能代码审查平台。

它接收 GitHub Webhook，拉取 PR diff，结合规则引擎、代码上下文和大语言模型，生成结构化 Review 报告，并可以自动评论到 GitHub PR。

一句话版本：

> CodeInsight = GitHub PR Diff + 规则引擎 + 代码上下文 + LLM Reviewer + 结构化报告 + CI/CD + Docker 部署。

这个项目适合写进简历，因为它同时覆盖：

- LLM 应用开发
- Agent / RAG 工程思维
- 后端 API
- 异步任务
- 高并发入口设计
- 规则引擎
- 自动化测试
- CI/CD
- Docker 部署
- 评测体系

## 2. 不要一开始就做大系统

新手最容易犯的错误是：一上来就做 LangGraph、多 Agent、Milvus、Kubernetes、Dashboard、复杂权限系统。

CodeInsight 的正确路线是先做最小闭环：

1. 本地启动 FastAPI。
2. 提供 `/review` 接口。
3. 输入一段模拟 PR diff。
4. 先跑确定性规则引擎。
5. 再调用 LLM 生成结构化 review。
6. 输出 JSON 报告。
7. 使用 pytest 测试核心模块。
8. 使用 GitHub Actions 自动跑测试。
9. 使用 Docker 启动服务。

只要这个闭环跑通，项目就从“文档壳”变成了“可展示工程”。

## 3. 当前目录应该怎么理解

```text
apps/
  api/        对外 HTTP 服务，使用 FastAPI，接收 webhook 和 review 请求
  worker/     后台任务服务，执行耗时的代码审查、LLM 调用、报告生成

core/
  github/     GitHub webhook 校验、PR diff 拉取、PR 评论发布
  parser/     代码解析，例如文件树、函数、类、AST、符号表
  retrieval/  上下文检索，例如找到和本次 diff 相关的文件或函数
  policy/     确定性规则引擎，例如禁止硬编码密钥、禁止危险 API
  reasoning/  LLM 审查逻辑，例如 bug/security/performance reviewer
  report/     结构化输出，例如 JSON report 和 Markdown PR comment

configs/
  models.yaml    模型配置
  rules.yaml     审查规则配置
  settings.yaml  系统配置

docs/
  项目愿景、架构、技术选型、ADR、RFC、开发指南

tests/
  单元测试、集成测试

evaluation/
  评测数据集、benchmark、评测指标

.github/
  GitHub Actions CI/CD 配置
```

## 4. MVP 功能范围

第一版不要追求真实生产全量能力。MVP 只做这些：

- `GET /health`：健康检查。
- `POST /review`：接收 diff，返回结构化审查结果。
- `policy engine`：执行 YAML 规则。
- `llm reviewer`：调用 LLM 生成建议。
- `report generator`：把审查结果转成 JSON 和 Markdown。
- `pytest`：覆盖核心模块。
- `GitHub Actions`：push 后自动跑测试。
- `Dockerfile`：支持容器启动。

MVP 暂时不做：

- 复杂前端 dashboard
- 多租户系统
- Kubernetes
- 大规模向量数据库集群
- 多 Agent 自主规划
- 完整权限管理

## 5. 推荐技术栈

| 模块 | 推荐选择 | 原因 |
| --- | --- | --- |
| Web 框架 | FastAPI | Python 生态友好，适合 AI 后端 |
| 测试 | pytest | 简单、成熟、适合单元测试 |
| 配置 | YAML + Pydantic | 易读且可校验 |
| 任务队列 | RQ 或 Celery | Webhook 快速返回，耗时任务后台执行 |
| 队列存储 | Redis | 部署简单，适合异步任务 |
| 数据库 | SQLite 起步，后续 PostgreSQL | 先降低复杂度，后续可迁移 |
| LLM 接入 | 抽象 ModelClient | 避免绑定单一供应商 |
| 向量库 | Qdrant 后续接入 | 部署轻，适合个人项目 |
| 部署 | Docker Compose | 比 Kubernetes 更适合 MVP |
| CI/CD | GitHub Actions | 和 GitHub 项目天然集成 |

## 6. 为什么先不用 Milvus

如果面试官问“为什么用 Qdrant 不用 Milvus”，可以这样回答：

> 我在 MVP 阶段选择 Qdrant，而不是 Milvus。原因是 Qdrant 部署更轻，Docker 单节点启动简单，Python SDK 易用，适合中小规模语义检索验证。Milvus 更适合大规模向量检索和复杂集群场景，但在当前阶段会增加运维复杂度。我的原则是先验证检索质量和业务闭环，再根据数据规模迁移。

重点不是背参数，而是体现你知道技术选型要考虑阶段、成本、复杂度和收益。

## 7. 高并发应该怎么做

不要说“支持百万并发”。这个项目更合理的高并发表达是：

1. Webhook 接口只做校验、入队和快速返回。
2. 耗时的 diff 分析、上下文构建、LLM 调用放到 worker。
3. Redis 队列削峰。
4. 使用任务 ID 查询审查状态。
5. 对 GitHub delivery id 或 PR commit sha 做幂等去重。
6. 对 LLM 调用设置超时、重试和限流。
7. 使用 k6 或 locust 压测 webhook 接口。

面试表达：

> 我没有把 LLM 审查放在 HTTP 请求线程里同步执行，因为 LLM 延迟不可控，会导致 webhook 堵塞。所以我采用 API + Queue + Worker 的结构，接口快速确认，后台异步处理，并用任务状态表追踪进度。

## 8. 30 天执行路线

### 第 1 周：最小闭环

| Day | 目标 |
| --- | --- |
| 1 | 搭建 FastAPI，完成 `/health` |
| 2 | 完成 `/review`，输入 fake diff |
| 3 | 实现 policy engine，先做 3 条规则 |
| 4 | 实现 LLM reviewer，输出 JSON |
| 5 | 实现 report generator，JSON 转 Markdown |
| 6 | 使用 pytest 测试 policy、review、report |
| 7 | 添加 Dockerfile 和 GitHub Actions |

### 第 2 周：接近真实业务

| Day | 目标 |
| --- | --- |
| 8 | 实现 GitHub webhook receiver |
| 9 | 实现 GitHub diff fetcher |
| 10 | 串起 PR review pipeline |
| 11 | 引入 Redis 队列和 worker |
| 12 | 添加任务状态查询接口 |
| 13 | 加日志、错误处理、重试 |
| 14 | 完善 README 和架构图 |

### 第 3 周：上下文和 LLM 能力

| Day | 目标 |
| --- | --- |
| 15 | 建立仓库文件索引 |
| 16 | 实现相关文件检索 |
| 17 | 提取函数、类、符号 |
| 18 | 实现 context builder |
| 19 | 拆分 bug/security/performance reviewer |
| 20 | 合并多个 reviewer 输出 |
| 21 | 建立 evaluation 数据集 |

### 第 4 周：工程化和上线

| Day | 目标 |
| --- | --- |
| 22 | Docker Compose 编排 API、Redis、Worker |
| 23 | GitHub Actions lint/test/build |
| 24 | 使用 k6 或 locust 压测 |
| 25 | 加限流和缓存 |
| 26 | 支持 GitHub PR comment |
| 27 | 输出评测报告 |
| 28 | 完善部署文档 |
| 29 | 清理项目结构和 README |
| 30 | 发布 v1.0 MVP |

## 9. 如何使用 LLM，但不让项目变成“全是 LLM 做的”

你可以让 LLM 写代码，但你要负责工程编排。

每次让 LLM 做一个小模块，并要求它输出：

1. 需求说明
2. 技术方案
3. 代码实现
4. 测试用例
5. 边界情况

你自己负责：

- 决定功能优先级
- 决定目录归属
- 拆分模块边界
- 运行测试
- 发现报错并要求修复
- 写 ADR 记录技术选择
- 做压测和评测
- 整理 README
- 做 CI/CD

这部分就是你简历和面试里真正能讲的内容。

## 10. 简历写法

项目名：

> CodeInsight - 面向 GitHub PR 的智能代码审查平台

项目描述：

> 基于 FastAPI、Redis Queue、LLM 和规则引擎实现的 PR 自动代码审查系统，支持 GitHub Webhook 接入、Diff 解析、上下文构建、结构化 Review 输出、异步任务处理、CI/CD 和 Docker 部署。

项目亮点：

- 设计 API + Worker 异步架构，将 Webhook 接收与 LLM 审查解耦，避免长耗时任务阻塞请求。
- 实现 YAML 规则引擎，在调用 LLM 前完成确定性检查，降低成本并提升可解释性。
- 构建结构化 Review Schema，输出 severity、file、line、reason、suggestion，便于自动评论到 PR。
- 使用 pytest 和 GitHub Actions 建立 CI 流程，覆盖 diff parser、policy engine、report generator 等核心模块。
- 使用 Docker Compose 编排 API、Redis、Worker，本地一键启动并支持部署。
- 构建小型评测集，对误报率、漏报率、响应延迟进行记录和迭代。

## 11. 面试时怎么讲这个项目

可以按照这个顺序讲：

1. 我想解决什么问题：PR review 重复、耗时、容易漏问题。
2. 我做了什么系统：Webhook 触发，异步分析，输出结构化报告。
3. 架构为什么这样设计：LLM 慢且不稳定，所以 API 和 Worker 解耦。
4. 为什么先规则后 LLM：规则便宜、稳定、可解释，LLM 处理语义和复杂推理。
5. 怎么保证质量：测试、CI、评测集、结构化输出、日志。
6. 怎么上线：Docker Compose、环境变量、GitHub Actions。
7. 后续怎么扩展：接入 Qdrant、AST 上下文、更多语言、多 reviewer。

## 12. 当前最重要的下一步

优先把项目从“文档骨架”推进到“能跑的 MVP”：

- FastAPI 服务
- `/health`
- `/review`
- policy engine
- structured report
- pytest
- GitHub Actions
- Dockerfile

当这 8 件事完成后，CodeInsight 就已经具备简历项目的基本可信度。
