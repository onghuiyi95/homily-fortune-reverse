# Homily Fortune (弘历 Fortune.EXE) — Signal Engine Reverse Engineering

逆向分析 **弘历 Fortune.EXE**（`C:\Program Files (x86)\Homily Fortune\Fortune.exe`，10.2 MB，2018-10-25）的「信号（Signal）」系统：它是怎样过滤股票、公式怎样计算、预警怎样运作。

> 配套公式引擎在 `CompMan-chs.dll`（同目录），本仓库聚焦 EXE 自身的信号编排与计算调度层。

---

## 0. TL;DR（给急着看结论的人）

- 弘历的「信号」= **参数化复合买点过滤器**：40+ 个原子技术指标条件，用户在对话框里勾选，按 **6 大类 OR-聚合**，再整体 **AND**，全为真才画黄色买点 `RGB(255,255,0)`。
- **无预存信号结果库**。指标由 `FormulaBase`/`FormulaCalc` 引擎**逐 K 线运行时现算**（证据：磁盘只有 `.day`/`.fen` 原始 OHLCV；EXE 内 `FormulaCalc.cpp`/`FormulaBase` 引擎 + 逐 bar 循环）。
- **改 filter → 重算**：条件选股模式下对范围内每只股票重新跑引擎（无结果缓存）。
- **预警常驻增量算**：加载方案后挂 `RecvSend-chs.dll` 实时主推，只对新到达的 bar 增量求值，不重跑全历史。
- 公式里的 `MACD.MACD`/`KDJ.K`/`HLTHBQ`/`HLTDMISTATIC`/`ISDEPART` 等算子由 `CompMan-chs.dll` 的 HLT 算子族提供实现；EXE 自身只做**公式解析 + 逐 bar 调度 + 结果 AND 门**。

---

## 1. 工具与方法

| 项 | 值 |
|---|---|
| 反编译器 | Ghidra 12.1.2（`analyzeHeadless` + `pyghidra`） |
| JDK | Microsoft Build of OpenJDK 21 (`_jdk21`) |
| 目标 | `Fortune.EXE`（PE32, x86, MFC 应用） |
| 提取手段 | ① EXE `.rdata` 内嵌公式字符串全文提取（无加密）② 51082 函数全量分析 + 聚焦区域反编译 |
| 对照真值 | 用户提供的信号配置对话框截图（Program=SS）、已逆的 `CompMan-chs.dll` HLT 算子族 |

> 注：函数名多为 MFC 混淆（`FUN_*`），文档用地址引用关键函数。

---

## 2. 信号总体架构

信号系统在 EXE 内的复合公式（字符串 `0x00894bc8`）：

```
:EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT AND
 PRICERESULT AND MOREKLINERESULT AND HLSIGNALRESULT,0,RGB(255,255,0)
```

即 **6 大类 GROUP 同时为真**才出黄色买点。6 组 ↔ UI 标签页（用户截图校准）：

| 复合变量 | UI 标签页 | 内容 |
|---|---|---|
| `EMARESULT` | **MA** | Distance Between MAs / MA 金死叉 / 指数&MA 关系 / MA 间关系 / 价格&MA / 红白圈 |
| `PROBABILILYRESULT` | **Probability** | 概率组（源码错别字 `PROBABILILY`，恒真 `:=1`） |
| `ENERGYRESULT` | **Energy** | 量能 / 换手 |
| `PRICERESULT` | **Quotation** | 价格 / 涨幅 / 振幅 / 高低 |
| `MOREKLINERESULT` | **Candlestick Pattern** | 更多 K 线形态 |
| `HLSIGNALRESULT` | **Homily Signals Group** | HLTHBQ 红白圈 / 通道 / KDJ-J / ZHSIGNAL / REDGREEN / TJ |
| （容器） | **Signal Program** | 命名 / 保存 / 加载整套信号方案（二进制 `0x378` 文件） |

⚠️ 关键：6 个 GROUP 在 EXE 公式常量里**全部 `:=1`（恒真）**（`0x0088e708` 等）。真正过滤由 40+ 个原子 `*RESULT` 条件在 C++ 里按用户勾选 OR-聚合决定。

---

## 3. 40+ 原子条件（完整清单）

详见 [`SIGNAL_LOGIC.md`](SIGNAL_LOGIC.md) 第二节。节选：

| 原子 | 公式 | 含义 |
|---|---|---|
| `MA22RESULT` | `HLTHBQ(C,1,1,1)` 上穿收盘价 | 红白圈红圈买点（= 之前逆的 HLTHBQ 双线穿越） |
| `MA23RESULT` | `HLTHBQ(C,1,1,1)` 下穿收盘价 | 白圈卖点 |
| `SIGNAL1RESULT` | KDJ 的 J 线上穿 50 | 买 |
| `ZHSIGNAL2RESULT` | 通道上轨上穿 + KDJ 金叉 + MACD 红柱放大 | 综合买 |
| `REDGREEN1RESULT` | 20 日 RSI 上穿 50 | |
| `TJ1RESULT` | 9 日 RSI 上穿 20 | 超卖回升 |
| `MA9RESULT` | `MACD>0 AND REF(MACD,1)<0` | MACD 上穿 0 轴 |
| `MA10RESULT` | `MACD>0 AND REF(MACD,1)<MACD` | 绿柱变长 |
| `VOL2RESULT` | `VOL>REF(VOL,1)>REF(VOL,2)` | 量递增 |
| `HAND2RESULT` | 上涨量占比区间 | 量能比 |

---

## 4. 公式计算核心逻辑（聚焦反编译铁证）

公式引擎 `FormulaBase` / `FormulaCalc.cpp` 位于 EXE `0x008eb918`–`0x008ec5c0`。
`0x008eb5c0`–`0x008eee80` 共 **13 个函数** = 算子实现层（合计 53 个 `do{...+=0xc}while` 逐记录循环 = 逐 K 线遍历）。

核心逐 K 线求值函数 `FUN_008eee80` 主干（剥异常壳）：

```c
double* CalcSeries(double* out, int* series, int len, int flag, uint* ok) {
    if (len == 0 || bars < 1) { *out = NAN; *ok = 0; return; }
    L = GetSeriesLen();                       // bar 数
    if (Validate(series) == 0 || L == 0) { *out = NAN; return; }
    EnterSeriesContext(series);
    getVal = (*(code**)(*series + 0xc));      // 算子: getValueAt(bar i)
    start = ...;
    int step = start * 0xc;                    // 每条记录 12 字节 (double)
    double* pd = buf + step;
    do {                                       // ← 逐 K 线循环
        if (*pd != NAN)
            out[step] = getValueAtBar(...);    // 调算子写结果
        step += 0xc;  pd += 0xc;               // 下一条 K 线
    } while (--remaining);
}
```

公式函数注册表 `FUN_009167a0` 把 `NETVALUE/ADVANCE/AMOUNT/CLOSE/COUNT/BARSLAST/HHVBARS/LLVBARS/BACKSET/BARSCOUNT/…` 全部注册进引擎词法表 → **引擎自带完整公式函数集，运行时解析执行，非预存**。

公式里的 `"MACD.MACD"(n1,n2,n3)` / `"KDJ.K"(n,3,3)` / `HLTHBQ(C,1,1,1)` / `HLTDMISTATIC(n,k)` / `ISDEPART(x,dir,m)` 是注册表里注册的**外部函数**，运行时由 `CompMan-chs.dll` 提供实现（即已逆的 HLT 算子族）。

详细伪代码见 [`formula_pseudocode.md`](formula_pseudocode.md)。

---

## 5. Filter 机制（你每次改 filter 为什么要等）

- **条件选股（手动跑）**：读本地 `.day`/`.fen` 全历史 → 对范围内每只股票 `for(stock)` 调 FormulaBase 引擎逐 K 线求值 → 末尾 AND 门判定。**无结果缓存** → 改一个勾也整体全重算，范围越大越慢。
- **预警（常驻）**：加载方案后问「要启动预警吗」→ 挂 `RecvSend-chs.dll` 实时主推 → 新数据到达（或按 `预警时间间隔` 轮询）**只对新 bar 增量算**，不重跑全历史。

> 唯一「不算」的是原始行情本身（已在本机）；公式数学每次都现算。

---

## 6. 预警系统

独立子系统，字符串证据齐全（`要启动预警吗`/`没运行预警`/`预警计算发生异常`/`预警消息响应发生异常`/`预警报告`/`预警股票加入/列出/删除发生异常`/`预警时间间隔`/`开机自动启动预警`）。实时数据来自 `RecvSend-chs.dll`（`YlsConnect`/`YlsIsConnect`/`YlsSendData`/`YlsGetConnectStatus`/`Yls_XHS`）。

详见 [`SIGNAL_LOGIC.md`](SIGNAL_LOGIC.md) 第六节。

---

## 7. 置信度分层

- **铁证（反编译 + 文件格式）**：无预存信号库；`FormulaBase`/`FormulaCalc.cpp` 引擎逐 K 线循环；`FUN_009167a0` 函数注册表；`FUN_008eee80` 的 `+=0xc` 逐 bar 写结果；公式算子名与 `CompMan-chs.dll` HLT 族对应；6 组 `:=1` 硬编码；UI 7 标签 ↔ 6 复合变量 + 方案容器。
- **高置信推论**：条件选股=`for(stock)` 全重算、预警=增量（由铁证 + 无信号库文件 + `预警时间间隔` 轮询参数推出）。
- **未坐实**：`for(stock)` 外层循环的精确 C++ 函数（被启动期函数指针表动态调用，Ghidra 静态 xref 未捕获 `FUN_009167a0` 调用者）。需运行时跟踪「选股执行」命令 handler 才能 100% 钉死。

---

## 8. 文件结构

```
.
├── README.md                  # 本文件
├── SIGNAL_LOGIC.md            # 详细逆向白皮书（架构/原子条件/预警/计算闭环）
├── formula_pseudocode.md      # 逐 K 线求值 + 原子条件 伪代码白皮书
├── _archive/                  # 中间产物（原始反编译、提取脚本），非人读
│   ├── decomp/                # 逐函数 Ghidra 反编译（含 MFC 噪声）
│   ├── extracts/              # 区域聚焦反编译（alert/formula/dialog）
│   └── all_functions.txt      # 全 51082 函数列表
└── ghidra_proj/               # Ghidra 工程（analyzeHeadless 产物，可忽略）
```

---

## 9. 免责声明

本仓库仅用于**安全研究 / 教育 / 指标复现**。逆向对象为闭源商业软件；公式实现归原厂所有。复现到 TradingView 等平台的 Pine Script 仅作算法对照，请遵守原厂许可与当地法律。
