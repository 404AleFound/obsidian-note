# Agent 数据结构

本文基于 `packages/agent/src/types.ts` 和 `packages/ai/src/types.ts`，整理 Agent 运行时使用的核心数据结构。Agent 层负责维护上下文、执行工具和分发事件，AI 层负责定义模型可以理解的标准消息。

## AgentContext

`AgentContext` 是一次 Agent Loop 运行时使用的上下文快照，包含系统提示词、对话记录和当前可用的工具。

```typescript
export interface AgentContext {
	/** 发送给模型的系统提示词。 */
	systemPrompt: string;
	/** 对话记录，对模型可见的上下文来源。 */
	messages: AgentMessage[];
	/** 本次运行可使用的工具。 */
	tools?: AgentTool<any>[];
}
```

需要注意：`messages` 的类型是 `AgentMessage[]`，因此其中可以包含应用自定义消息；真正调用模型前，还需要通过 `convertToLlm` 将它们转换为模型支持的 `Message[]`。

## AgentTool

`AgentTool` 是 Agent 可以调用的工具定义。它同时包含工具描述、参数 schema 和实际执行函数。

```typescript
export interface AgentTool<
	TParameters extends TSchema = TSchema,
	TDetails = any,
> extends Tool<TParameters> {
	name: string;
	description: string;
	parameters: TParameters;
	/** 用于界面展示的工具名称。 */
	label: string;
	/** 在参数校验前兼容或修正模型生成的原始参数。 */
	prepareArguments?: (args: unknown) => Static<TParameters>;
	/** 执行工具并返回结果。 */
	execute: (
		toolCallId: string,
		params: Static<TParameters>,
		signal?: AbortSignal,
		onUpdate?: AgentToolUpdateCallback<TDetails>,
	) => Promise<AgentToolResult<TDetails>>;
	/** 覆盖全局的工具执行模式。 */
	executionMode?: "sequential" | "parallel";
}
```

其中，`name`、`description` 和 `parameters` 来自 AI 层的 `Tool`；`parameters` 是 TypeBox schema，用于校验模型传入的参数。Agent 会先查找工具、准备并校验参数，然后才调用 `execute`。

### AgentToolResult

工具执行函数返回 `AgentToolResult<TDetails>`：

```typescript
export interface AgentToolResult<TDetails> {
	/** 返回给模型的文本或图片。 */
	content: (TextContent | ImageContent)[];
	/** 供日志和 UI 使用的结构化详情。 */
	details: TDetails;
	/** 工具自身产生的 token 使用量，不参与主模型上下文统计。 */
	usage?: Usage;
	/** 从当前上下文位置开始新增可用的工具。 */
	addedToolNames?: string[];
	/** 是否提示 Agent 在当前工具批次后停止。 */
	terminate?: boolean;
}
```

`AgentToolResult` 会被转换成 `ToolResultMessage` 并追加到上下文中。工具失败时，Agent 会捕获异常并生成 `isError: true` 的工具结果。

## AgentMessage

`AgentMessage` 是 Agent 内部统一使用的消息类型，用于表示用户输入、模型回复、工具结果和应用自定义消息。它是一个联合类型，而不是单一的对象结构：

```typescript
export type AgentMessage =
	| Message
	| CustomAgentMessages[keyof CustomAgentMessages];

export type Message =
	| UserMessage
	| AssistantMessage
	| ToolResultMessage;
```

消息通过 `role` 字段区分类型。
### UserMessage

```typescript
export interface UserMessage {
	role: "user";
	content: string | (TextContent | ImageContent)[];
	timestamp: number;
}
```

`content` 可以是普通字符串，也可以是文本和图片内容块的数组。

### AssistantMessage

```typescript
export interface AssistantMessage {
	role: "assistant";
	content: (TextContent | ThinkingContent | ToolCall)[];
	api: Api;
	provider: ProviderId;
	model: string;
	responseModel?: string;
	responseId?: string;
	diagnostics?: AssistantMessageDiagnostic[];
	usage: Usage;
	stopReason: StopReason;
	deferred?: DeferredHandle;
	errorMessage?: string;
	rawStopReason?: string;
	endTurn?: boolean;
	timestamp: number;
}
```

`content` 可以包含三类内容：

- `TextContent`：模型生成的文本，结构为 `{ type: "text", text: string }`。
- `ThinkingContent`：模型的思考内容，结构为 `{ type: "thinking", thinking: string }`。
- `ToolCall`：模型请求 Agent 执行工具的调用块。

`usage` 记录输入、输出、缓存和费用等统计信息；`stopReason` 表示模型停止的原因，例如 `stop`、`toolUse`、`length`、`error` 或 `aborted`。

### ToolResultMessage

```typescript
export interface ToolResultMessage<TDetails = any> {
	role: "toolResult";
	toolCallId: string;
	toolName: string;
	content: (TextContent | ImageContent)[];
	details?: TDetails;
	usage?: Usage;
	addedToolNames?: string[];
	isError: boolean;
	timestamp: number;
}
```

`toolCallId` 必须对应 `ToolCall.id`，`toolName` 对应被调用工具的名称。这样模型和 Agent 才能将工具结果关联到正确的调用。

### 自定义消息

`CustomAgentMessages` 默认是空接口，应用可以通过 TypeScript declaration merging 扩展它：

```typescript
declare module "@earendil-works/pi-agent-core" {
	interface CustomAgentMessages {
		notification: {
			role: "notification";
			text: string;
			timestamp: number;
		};
	}
}
```

自定义消息可以保存在 Agent 上下文中，但模型通常不能直接理解它们。调用模型前，应在 `convertToLlm` 中将其转换成标准消息，或者将其过滤掉。

### AgentMessage 的转换流程

```text
AgentMessage[]
    ↓ transformContext（可选）
AgentMessage[]
    ↓ convertToLlm（必需）
Message[]
    ↓
模型 API
```

`transformContext` 适合做上下文裁剪和外部信息注入；`convertToLlm` 负责过滤 UI 消息、转换自定义消息，并确保最终结果只包含模型支持的消息类型。

## AgentToolCall

`AgentToolCall` 表示模型在 `AssistantMessage.content` 中生成的一次工具调用请求。它不是独立的消息，而是助手消息中的一种内容块。

```typescript
export type AgentToolCall = Extract<
	AssistantMessage["content"][number],
	{ type: "toolCall" }
>;
```

其实际结构来自 AI 层的 `ToolCall`：

```typescript
export interface ToolCall {
	type: "toolCall";
	id: string;
	name: string;
	arguments: Record<string, any>;
	thoughtSignature?: string;
	namespace?: string;
}
```

字段说明：

- `type`：固定为 `"toolCall"`，用于从助手内容块中识别工具调用。
- `id`：本次调用的唯一 ID，工具结果通过 `toolCallId` 与它关联。
- `name`：工具名称，对应 `AgentTool.name`。
- `arguments`：模型生成的原始参数。Agent 会先执行 `prepareArguments`（如果存在），再依据 `parameters` schema 校验。
- `thoughtSignature`：部分模型提供商使用的思考签名，用于保持思考上下文连续性。
- `namespace`：OpenAI Responses API 中动态工具或命名空间工具使用的可选字段。

示例：

```typescript
const toolCall: AgentToolCall = {
	type: "toolCall",
	id: "call_123",
	name: "read_file",
	arguments: { path: "package.json" },
};
```

调用关系如下：

```text
AssistantMessage.content
        ↓
AgentToolCall
        ↓ 参数准备与校验
AgentTool.execute()
        ↓
ToolResultMessage
```

`AgentToolCall` 是“模型想做什么”，`AgentTool` 是“Agent 能做什么”，`AgentToolResult` 是“工具执行后返回什么”。

## AgentLoopConfig

`AgentLoopConfig` 是低层 Agent Loop 的运行配置。它继承 `SimpleStreamOptions`，因此还包含模型请求相关的通用选项，例如 API key、请求超时、最大 token 数和推理级别等。

```typescript
export interface AgentLoopConfig extends SimpleStreamOptions {
	model: Model<any>;
	convertToLlm: (messages: AgentMessage[]) => Message[] | Promise<Message[]>;
	transformContext?: (
		messages: AgentMessage[],
		signal?: AbortSignal,
	) => Promise<AgentMessage[]>;
	getApiKey?: (provider: string) => Promise<string | undefined> | string | undefined;
	shouldStopAfterTurn?: (
		context: ShouldStopAfterTurnContext,
	) => boolean | Promise<boolean>;
	prepareNextTurn?: (
		context: PrepareNextTurnContext,
	) => AgentLoopTurnUpdate | undefined | Promise<AgentLoopTurnUpdate | undefined>;
	getSteeringMessages?: () => Promise<AgentMessage[]>;
	getFollowUpMessages?: () => Promise<AgentMessage[]>;
	toolExecution?: "sequential" | "parallel";
	beforeToolCall?: (
		context: BeforeToolCallContext,
		signal?: AbortSignal,
	) => Promise<BeforeToolCallResult | undefined>;
	afterToolCall?: (
		context: AfterToolCallContext,
		signal?: AbortSignal,
	) => Promise<AfterToolCallResult | undefined>;
}
```

关键字段的作用：

- `model`：下一次请求使用的模型。
- `convertToLlm`：必需的消息转换器。它必须将 `AgentMessage[]` 转换为模型能理解的标准 `Message[]`。
- `transformContext`：在消息转换前裁剪或修改 Agent 上下文。
- `getApiKey`：每次模型请求动态获取 API key，适合会过期的 OAuth token。
- `shouldStopAfterTurn`：当前 turn 完成后决定是否优雅停止。若返回 `true`，不会再发起下一次模型请求。
- `prepareNextTurn`：下一次 turn 开始前替换上下文、模型或推理级别。
- `getSteeringMessages`：Agent 执行过程中注入控制消息。
- `getFollowUpMessages`：当前工作完成后追加后续消息。
- `toolExecution`：工具执行模式，`parallel` 为默认值；`sequential` 表示逐个执行。
- `beforeToolCall`：参数校验后、工具执行前调用，可通过 `{ block: true }` 阻止执行。
- `afterToolCall`：工具执行后、结果事件发出前调用，可覆盖结果内容、详情、错误状态等字段。

### 相关回调数据结构

```typescript
export interface ShouldStopAfterTurnContext {
	message: AssistantMessage;
	toolResults: ToolResultMessage[];
	context: AgentContext;
	newMessages: AgentMessage[];
}

export interface PrepareNextTurnContext extends ShouldStopAfterTurnContext {}

export interface AgentLoopTurnUpdate {
	context?: AgentContext;
	model?: Model<any>;
	thinkingLevel?: ThinkingLevel;
}
```

`PrepareNextTurnContext` 没有新增字段，只是复用 `ShouldStopAfterTurnContext` 的结构。它表示当前 turn 已完成、但 Agent 还准备继续运行时的状态。

工具回调的上下文包含：请求工具调用的 `assistantMessage`、原始 `toolCall`、通过 schema 校验后的 `args`、当前 `context`，以及 `afterToolCall` 中的工具执行结果 `result`。

## AgentEvent

`AgentEvent` 是 Agent 对外发布的事件联合类型，使用 `type` 字段进行区分，主要服务于 UI 更新、会话持久化和运行状态监控。

```typescript
export type AgentEvent =
	| { type: "agent_start" }
	| { type: "agent_end"; messages: AgentMessage[] }
	| { type: "turn_start" }
	| { type: "turn_end"; message: AgentMessage; toolResults: ToolResultMessage[] }
	| { type: "message_start"; message: AgentMessage }
	| {
			type: "message_update";
			message: AgentMessage;
			assistantMessageEvent: AssistantMessageEvent;
	  }
	| { type: "message_end"; message: AgentMessage }
	| { type: "tool_execution_start"; toolCallId: string; toolName: string; args: any }
	| { type: "tool_execution_update"; toolCallId: string; toolName: string; args: any; partialResult: any }
	| { type: "tool_execution_end"; toolCallId: string; toolName: string; result: any; isError: boolean };
```

事件可以分为四组：

| 事件组 | 事件 | 作用 |
| --- | --- | --- |
| Agent 生命周期 | `agent_start`、`agent_end` | 标记一次完整 Agent 运行的开始和结束 |
| Turn 生命周期 | `turn_start`、`turn_end` | 一个 turn 包含一次助手回复及其工具调用和结果 |
| 消息生命周期 | `message_start`、`message_update`、`message_end` | 追踪用户、助手和工具结果消息；`message_update` 只用于助手流式回复 |
| 工具生命周期 | `tool_execution_start`、`tool_execution_update`、`tool_execution_end` | 追踪工具开始、进度更新和最终结果 |

一次包含工具调用的典型事件顺序如下：

```text
agent_start
  └─ turn_start
      ├─ message_start / message_end       用户消息
      ├─ message_start / message_update... / message_end  助手消息
      ├─ tool_execution_start
      ├─ tool_execution_update...          可选
      ├─ tool_execution_end
      ├─ message_start / message_end       工具结果消息
      └─ turn_end
  └─ 下一轮 turn，或 agent_end
```

在并行工具执行模式下，`tool_execution_end` 按工具完成顺序发出；最终追加到上下文的工具结果消息仍按助手消息中工具调用的原始顺序排列。`agent_end` 是一次运行发出的最后一个 Agent 事件。
