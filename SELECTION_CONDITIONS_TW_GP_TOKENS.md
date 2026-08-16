# 拐点操盘 exp token 映射推断（Turtle Winner TechnicalIndex1.exp）

> ⚠️ 置信度分层：底层算子(HLTHLP/HLTHBQ/ISDEPART/XTWBREAK)已铁证反编译；以下拐点的"复合公式"真源码在 exp 私有 token 里，
> 拼音算子(YXXHEH/AHEH/ZRU 等)不在 dll 字符串表，是编译器内部代号。**下列映射为结构对齐推断，非铁证**。

## 已知铁证 token（dll 反编译确认）
- `YDHYAD` = HLTHLP（六彩神龙获利盘，FUN_100c0b20，窗口100/阈值0.97/×100）
- `2b2427` = CLOSE, `4025` = MA, `5255` = DMA(动态均线), `5254` = HHV, `5253` = LLV, `2d563a` = REF
- `Y0VXH` = HIGH（背离公式确认）, `ZVXDXD` = LOW（背离公式确认）, `DYPAAG` = MA, `BYXX` = CLOSE, `DEYDXAD` = EMA/平滑
- `Y0GN2` = 常数/周期N, `Y0RU` = 某计算

## 结构对齐推断（拐点操盘 vs 背离对照）
| token | 推断含义 | 依据 |
|---|---|---|
| `AHEH` | `REF` 或 `HHV` 类（接收 CLOSE,1 后跟 AAHGH）| 在 `AHEHCLOSE,1AAHGH` 结构，类似背离 `DYPAAG(CLOSE)` |
| `AAHGH` | 窗口/系数（紧跟价格序列）| `AHEHCLOSE,1AAHGH` 中 AAHGH 是第二参数 |
| `YXXHEH` | 价格算子（HIGH/LOW 类，与 `YXX` 同源）| `YXXHEH((QXHBH` 一元调用 |
| `QXHBH` | `CROSS` 或计算算子 | `YXXHEH((QXHBH(...` |
| `ZRU` / `ZYRU` | 拐点/穿越判定算子（核心）| 在 `YDHYAD` 后做拐点判定 `ZRU1+(...` |
| `YXZDXD` | LOW 类（与 `ZVXDXD`=LOW 同源）| `YXZDXD` `Z`+`XD`=低 |
| `QAAG` | MA 类（与 `DYPAAG`=MA 同源）| `QAAG(--QAE` |
| `QAE` | 周期参数 | `QAAG(--QAE` |
| `DXDZS` | 差分/变化率 | `...DXDZS` |
| `TQXH` / `VYXH` | 通道上/下轨 | `TQXH*1` `VYXH*1` |
| `DYAV` / `DZAV` | 斜率/角度 | `DYAV**1` `DZAV` |
| `AABXF` | 系数/阈值 | `AABXF` |
| `HLT3` | 拐点操盘自身标记（HLT-3 类）| 末尾 `HLT3(` |
| `O2OAD` | 未明（可能是 `OR` 或窗口）| `YDH-O2OAD` |

## 拐点操盘 结构伪代码（推断版，对照 token decode）
```
// 拐点操盘 = 六彩神龙(HLTHLP) 穿越 弘历进出(HLTHBQ) 的拐点判定
// 核心：ZRU(拐点算子) 检测 YDHYAD(获利盘) 与 动态均线(DMA) 的穿越

HLTHLP_val = YDHYAD  // 六彩神龙获利盘 (铁证)

// AHEH/AAHGH 构造的线（推断：动态参考线）
LineA = AHEH(CLOSE, 1) AAHGH   // 推断: REF/HHV(CLOSE,1) 类
LineB = AHEH(LineB, N) AAHGH   // 推断
LineC = AHEH(LineC, N)         // 推断

// ZRU = 拐点判定：获利盘 上穿/下穿 参考线
拐点上 = ZRU(YXXHEH(QXHBH(HLTHLP_val, LineA)), ...)
拐点下 = ZRU(...)

// DMA 动态均线平滑
DMA_line = DMA(CLOSE, N)  // 铁证 DMA token
// TQXH/VYXH = 通道上下轨（推断）
通道上 = TQXH * 1
通道下 = VYXH * 1

// 最终：HLT3(拐点操盘) = 获利盘穿越均线 + 通道突破
拐点操盘结果 = HLT3( ... )
```

## 诚实结论
- **铁证**：拐点操盘底层 = HLTHLP(获利盘) + HLTHBQ(红白圈) + DMA + MA + ISDEPART(背离)，全部已反编译。
- **推断**：拐点操盘复合公式的私有 token(ZRU/AHEH/AAHGH/QXHBH 等) 不在 dll 字符串表，是编译器内部代号。
  结构对齐给出上述推断，但**不能直接翻成可验证的 Pine**（缺乏每个 token 的精确定义）。
- **要拿到拐点操盘真数值公式**：需你提供 Turtle Winner 公式编辑器里"拐点操盘"的源码（截图/文本），或反编译 dll 里对应的 HLT-1/HLT-3 计算函数（如果存在）。

## 原始提取
- `_archive/tw_gp_all_tokens.txt`（10 个拐点公式的完整 token decode，含 拐点操盘/海龟买卖/龙宫九子/背离/分形/持安/活跃突破/四重底部/智能交易/终极震荡）

> ⚠️ 勘误：YDHYAD 是 token_decode_v4 误读 token 字节流伪造的显示（非真实函数名，dll/exe 无此字符串）。相关推断作废。
