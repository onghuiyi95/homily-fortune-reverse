# 弘历 Fortune.EXE — 信号系统全逻辑（逆向完整版）

> 逆向对象：`C:\Program Files (x86)\Homily Fortune\Fortune.exe`（10.2 MB，2018-10-25，MFC/PE32）
> 方法：Ghidra 12.1.2 + pyghidra 全量分析反编译（51082 函数） + EXE `.rdata` 内嵌公式字符串提取
> 配套公式引擎：`CompMan-chs.dll`（同目录，提供 HLT 算子实现）
> 本文件汇总全部已逆证逻辑；每条标注「铁证 / 高置信 / 未坐实」。

---

## 0. 一句话总览

弘历的「信号」= **参数化复合买点过滤器**：73 个原子技术指标条件，用户在对话框按 6 大类勾选，引擎对股票范围内每只股**逐 K 线运行时求值**，组内 AND、组间 AND，**所有勾选条件同真**才画黄色买点。无预存信号库；改 filter 必全重算；预警常驻增量算。

---

## 1. 数据层（无预存信号）

| 项 | 内容 | 性质 |
|---|---|---|
| 本地行情格式 | `.day`(日线) / `.min`·`.nmn`(分钟) / `.fen`(分时) / `.qte`(自选) | 原始 OHLCV |
| `.fen` 头 | `magic=12344321` + 日期 + 记录数 + float OHLCV（实测 `24368.fen`：20181025 / 5769 根） | 铁证 |
| 信号结果库 | **不存在**（无 `.sig`/signal cache 格式） | 铁证 |
| `HelpID-enu.cfg` | 明文：`This analysis is based on the local candlestick data` | 铁证 |

→ 结论：**指标由 FormulaBase 引擎运行时算，不是查预存表**。

---

## 2. 公式引擎层（FormulaBase / FormulaCalc.cpp）

| 项 | 地址 | 性质 |
|---|---|---|
| 引擎类字符串 | `0x008eb918` `FormulaCalcl` / `0x008ec5c0` `FormulaBase` | 铁证 |
| 算子实现层 | `0x008eb5c0`–`0x008eee80`（13 函数，53 个 `do{...+=0xc}while` 逐记录循环） | 铁证 |
| 逐 K 线求值主函数 | `FUN_008eee80`（`+=0xc` 指针循环，每根 K 线调 `getValueAt(i)` 写结果数组） | 铁证 |
| 公式函数注册表 | `FUN_009167a0`（注册 `CLOSE/COUNT/BARSLAST/HHVBARS/LLVBARS/BACKSET/…` 内建函数） | 铁证 |

**逐 K 线求值伪代码**（剥异常壳）：
```c
double* CalcSeries(double* out, int* series, int len, int flag, uint* ok) {
    spj_len = GetTotalBars();
    if (len == 0 || spj_len < 1) { *out = NAN; *ok = 0; return; }
    L = GetSeriesLen(series);
    if (ValidateSeries(series)==0 || L==0) { *out = NAN; return; }
    EnterSeriesContext(series);
    getVal = series->vtbl[3];            // getValueAt(bar i)
    step = start * 0xc;                  // 每条 12 字节
    pd = buf + step;  remaining = L - start;
    do {                                  // ← 逐 K 线
        if (*pd != NAN) out[step] = getVal(series, current_bar);
        step += 0xc;  pd += 0xc;
    } while (--remaining);
    return out;
}
```
→ `REF(X,1)`=`getValueAt(i-1)`；`LLV(LOW,9)`=窗口 min；`SMA(...,3,1)`=窗口递归平滑。

**外部算子（dll 提供）**：`"MACD.MACD"`/`"MACD.DIFF"`/`"MACD.DEA"`/`"KDJ.K"`/`"KDJ.D"`/`"KDJ.J"`/`"W&R"`/`"RSI.RSI1"`/`HLTHBQ`/`HLTDMISTATIC`/`ISDEPART`。EXE 自身只做**公式解析 + 逐 bar 调度 + 结果 AND 门**。

---

## 3. 选股逻辑（复合门控 + 组内/组间 AND）

### 3.1 最终买点（复合公式字符串 @ `0x00894bc8`，铁证）
```
:EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT AND
 PRICERESULT AND MOREKLINERESULT AND HLSIGNALRESULT,0,RGB(255,255,0)
```
6 大类（铁证，全部 `:=1` 恒真）：
| 变量 | UI 标签 | 地址 |
|---|---|---|
| `EMARESULT` | MA | `0x0088fc0c` |
| `PROBABILILYRESULT` | Probability（拼错，恒真） | `0x008912fc` |
| `ENERGYRESULT` | Energy | `0x0088e708` |
| `PRICERESULT` | Quotation | `0x00890a24` |
| `MOREKLINERESULT` | Candlestick Pattern（恒真） | `0x0088f6ec` |
| `HLSIGNALRESULT` | Homily Signals Group | `0x0088ed04` |
| （容器） | Signal Program（方案保存/加载） | — |

### 3.2 组内 AND、组间 AND（铁证，来自 `.rdata` 模板链）
每组是一条用 `AND` 固定串联的模板链，链尾恒真 `:=1`：
```
... AND MA11RESULT AND MA10RESULT ... AND MA1RESULT        EMARESULT:=1
... AND CLOSE11RESULT ... AND CLOSE1RESULT AND MARKETVALUERESULT   PRICERESULT:=1
... AND KDJ7RESULT ... AND KDJ1RESULT AND DMI2RESULT ... AND RSI1RESULT   PROBABILILYRESULT:=1
... AND VOL6RESULT ... AND VOL1RESULT                      ENERGYRESULT:=1
```
**机制**：勾选条件 N → 仅把 `XRESULT:=1` 替换为 `XRESULT:=<真实公式>`；未勾选保持 `:=1`（恒真）。整链 AND ⇒ **所有勾选条件必同时为真才过该类 = 组内 AND**。组间也是 AND。

→ **勾选 = 收紧过滤**（与"OR 越勾越松"相反）。未勾选的组恒真放行。

---

## 4. Filter 机制（你每次改 filter 为什么要等）

- **条件选股（手动跑）**：读本地 `.day`/`.fen` 全历史 → `for(stock)` 调 FormulaBase 逐 K 线求值 → 末尾 AND 门判定。**无结果缓存** ⇒ 改一个勾也整体全重算，范围越大越慢。
- **预警（常驻）**：加载方案后挂 `RecvSend-chs.dll` 实时主推，只对新到达 bar 增量算，不重跑全历史。

> 唯一「不算」的是原始行情本身（已在本机）；公式数学每次现算。

---

## 5. 预警系统（独立子系统）

| 字符串 | 地址 | 性质 |
|---|---|---|
| `要启动预警吗` | `0x008610ac` | 铁证 |
| `没运行预警` | `0x00860794` | 铁证 |
| `预警计算发生异常` / `预警消息响应发生异常` | `0x00860760` / `0x008606e7` | 铁证 |
| `预警报告` / `预警股票加入/列出/删除发生异常` | `0x0086105c` / `0x008611dc` 等 | 铁证 |
| `预警时间间隔` / `开机自动启动预警` | `0x008ee3e3` / `0x008ee4a0` | 铁证 |

实时数据层 `RecvSend-chs.dll` 导出：`YlsConnect`/`YlsIsConnect`/`YlsSendData`/`YlsGetConnectStatus`/`Yls_XHS`（弘历自研行情通信层）。

**机制（高置信）**：方案加载后常驻线程，新数据到达（或按 `预警时间间隔` 轮询）对监控池增量求值，命中弹「预警报告」+提示。由铁证（无信号库 + `预警时间间隔` 轮询参数 + RecvSend 主推）推出。

> 预警对话框 UI 处理函数（`FUN_00860f60` 等）已反编译，确认是启动/确认入口；真正计算循环在引擎层复用 §2，按新 bar 增量调用 `FUN_008eee80`。

---

## 6. 73 个原子条件（完整清单见 SELECTION_CONDITIONS.md）

按 6 组分布：
- **MA**（23）：MA1–MA23（两均差/金死叉/乖离/布林/MACD 金死叉·0轴·红绿柱/HLTHBQ 红白圈）
- **Probability**（0）：恒真占位
- **Energy**（7）：HAND1/2 + VOL1–6
- **Quotation**（14）：CLOSE1–14 + MARKETVALUE
- **Candlestick**（0）：复合恒真；承载 KDJ/RSI/WR/DMI 子类
- **Homily Signals**（23+）：SIGNAL1–4 / KDJ1–7 / RSI1–5 / WR1–3 / DMI1–2 / ZHSIGNAL1–2 / REDGREEN1–2 / TJ1–2
- **背离 4 条（KDJ4/KDJ5/RSI2/RSI3，调用 `ISDEPART`）**：公式层调用壳存在，但**全软件栈均未实现**——三版 Fortune dll + 盛世赢家II dll 字符串扫描 0 命中，且 EXE 中 `ISDEPART` 4 处字符串 Ghidra xref = 0（未注册、未实现），实际降级不生效。详见 SELECTION_CONDITIONS.md §G。

节选（公式原文均来自 `.rdata`，铁证）：
- `MA22RESULT = HLTHBQ(C,1,1,1)` 白圈转红 = 买点
- `MA10RESULT = "MACD.MACD">0 AND REF(.,1)<MACD` = 红柱变长
- `SIGNAL1RESULT` = KDJ 的 J 线上穿 50
- `ZHSIGNAL2RESULT` = 通道上穿 + KDJ 金叉 + MACD 红柱放大
- `TJ1RESULT` = 9 日 RSI 上穿 20（超卖回升）

---

## 7. 方案持久化（信号方案文件）

| 函数 | 地址 | 内容 |
|---|---|---|
| 方案加载/保存 | `FUN_0088fb60` | 读 `0x378` 二进制方案文件，`FUN_008a5b30` 按编号查条件工厂 |
| 条件工厂 | `FUN_008a5b30` | 从函数指针表取第 N 个原子条件计算函数 |

→ 方案文件存的是**勾选了哪些条件 + 参数**，不是算好的结果。

---

## 8. 计算路径闭环

```
本地 .day/.fen (原始OHLCV, 无预存信号库)
   → 条件选股: for(每只股) 调 FormulaBase
       → FUN_008eee80 逐 K 线循环求值每个 *RESULT
       → 组内 AND (勾选=替换:=1 为公式) / 组间 AND
       → 全真 → 黄色买点
   预警: 同引擎, 只对新 bar 增量算 (不重跑全历史)
```

---

## 9. 置信度总表

| 结论 | 层级 |
|---|---|
| 无预存信号库；行情为原始 OHLCV | 铁证 |
| 73 原子公式原文（`.rdata` 明文） | 铁证 |
| 6 组 `:=1` 恒真；复合 AND 门 `0x00894bc8` | 铁证 |
| 组内 AND / 组间 AND（`.rdata` AND 链模板） | 铁证 |
| 逐 K 线求值（`FUN_008eee80` `+=0xc` 循环） | 铁证 |
| 公式函数注册表（内建函数集） | 铁证 |
| 预警 = 增量算（非全重算） | 高置信（由铁证 + 轮询参数推出） |
| `for(stock)` 外层循环精确 C++ 函数 | 未坐实（启动期函数指针动态调用，静态 xref 未捕获） |
| ISDEPART 背离数学 | **铁证：全软件栈未实现**（三版 Fortune dll + 盛世赢家II dll 字符串 0 命中；EXE 中 `ISDEPART` 4 处字符串 Ghidra xref = 0，未注册/未实现；4 条背离条件降级不生效） |

---

## 10. 文件索引

```
README.md                 项目说明 + 方法 + TL;DR
SIGNAL_LOGIC.md           详细白皮书（架构/计算闭环/预警）
SELECTION_CONDITIONS.md   73 原子条件完整清单 + 选股 OR/AND 逻辑
formula_pseudocode.md     逐 K 线求值 + 原子条件 伪代码（TV 对照风格）
FULL_LOGIC.md             本文件（全逻辑汇总）
_archive/                 中间产物（原始反编译、提取脚本），非人读
```

---

## 11. 免责声明

仅用于安全研究 / 教育 / 指标复现。逆向对象为闭源商业软件；公式实现归原厂所有。复现到 TradingView 等平台的 Pine Script 仅作算法对照，请遵守原厂许可与当地法律。
