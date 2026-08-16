# 公式引擎伪代码白皮书（Formula Pseudocode）

供对着 TradingView 报错逐行核对用的伪代码。风格：`spj = close[i]  // 当前收盘价` 带 `//` 注释。

---

## A. 逐 K 线求值主循环（FUN_008eee80 @ 0x008eee80）

这是 FormulaBase 引擎对「一只股票的某条公式」求值的真实 C++ 逻辑（已剥 MFC 异常壳）。

```c
// ===== CalcSeries: 对一条序列(公式)逐 bar 求值 =====
double* CalcSeries(double* out, int* series, int len, int flag, uint* ok) {
    spj_len = GetTotalBars();            // 该股票总 K 线数
    if (len == 0 || spj_len < 1) {       // 无数据
        *out = NAN;
        *ok  = 0;
        return out;
    }
    L  = GetSeriesLen(series);           // 序列长度(bar 数)
    L2 = GetSeriesLen(series);
    if (ValidateSeries(series) == 0 || L == 0 || L2 == 0) {
        *out = NAN;
        return out;
    }
    EnterSeriesContext(series);          // 把该序列设为"当前序列"，后续 REF/LLV 都基于它
    getVal = series->vtbl[3];            // vtable+0xc: getValueAt(bar i) —— 算子取第 i 根值
    first = getVal(series, 0);           // 第 0 根 bar 的值
    last  = getVal(series, L2);          // 最后一根 bar 的值
    start = ...;                         // 起始 bar（对齐/前置 NaN 处理）
    step  = start * 0xc;                 // 每条记录 12 字节 = 一个 double
    pd    = buf + step;
    remaining = L - start;
    do {                                  // ← 逐 K 线循环（铁证）
        if (*pd != NAN) {
            out[step] = getVal(series, current_bar);   // 算子在第 current_bar 根的值写入结果
        }
        step += 0xc;                      // 指针 +12 字节 → 下一根 K 线
        pd   += 0xc;
    } while (--remaining != 0);
    return out;
}
```

**关键语义**：
- `series->vtbl[3]` = `getValueAt(i)`：把 bar 下标 `i` 喂给算子，返回该 bar 的值。
- `REF(X,1)` = `getValueAt(current_bar - 1)`；`LLV(LOW,9)` = 在 `[current_bar-8 , current_bar]` 窗口取 min；`SMA(...,3,1)` = 该窗口上的递归平滑。
- 输出 `out[]` 是长度相等的结果数组，每个元素 = 该 bar 的条件真假/数值。

---

## B. 公式函数注册表（FUN_009167a0 @ 0x009167a0）

引擎启动期把内建函数逐个注册进词法表（节选）：

```c
RegisterFunc("NETVALUE",  0xdb);   // 净值
RegisterFunc("ADVANCE",   0xcb);   // 涨数
RegisterFunc("AMOUNT",    0xcc);   // 额
RegisterFunc("ASKPRICE",  0xcd);
RegisterFunc("ASKVOL",    0xce);
RegisterFunc("BIDPRICE",  0xcf);
RegisterFunc("BIDVOL",    0xd0);
RegisterFunc("BUYVOL",    0xd1);
RegisterFunc("CLOSE",     0xd2);   // ← 收盘价，公式里 CLOSE 走这里
RegisterFunc("DECLINE",   0xd3);
RegisterFunc("EXTDATA",   0xd4);   // 扩展数据(1-11)
RegisterFunc("ISBUYORDER",0xd6);
RegisterFunc("SELLVOL",   0xd9);
RegisterFunc("BARSTATUS", 0xdc);   // 1=第一根 2=最后一根
RegisterFunc("MINUTE",    0xe3);
RegisterFunc("MONTH",     0xe4);
RegisterFunc("WEEKDAY",   0xe6);
RegisterFunc("BACKSET",   0xeb);
RegisterFunc("BARSCOUNT", 0xec);   // 当前 bar 序号
RegisterFunc("BARSLAST",  0xed);   // 上一次条件成立距现在的 bar 数
RegisterFunc("BARSSINCE", 0xee);
RegisterFunc("COUNT",     0xef);   // COUNT(X,N): N 根内 X 为真次数
RegisterFunc("HHVBARS",   0xf3);
RegisterFunc("LLVBARS",   0xf5);
// ... 共约 0x2f+ 个内建函数
```

→ 这些是公式语言的关键字。`CLOSE`/`COUNT`/`BARSLAST`/`HHVBARS` 等都能在用户条件公式里直接用，引擎运行时解析。

---

## C. 外部算子（由 CompMan-chs.dll 提供）

公式里带引号/大写名的算子，在注册表注册为「外部函数」，实现在 `CompMan-chs.dll`：

| 公式写法 | 参数 | dll 实现 | 语义 |
|---|---|---|---|
| `"MACD.MACD"(n1,n2,n3)` | 快/慢/信号 EMA | MACD 标准 | MACD 柱 |
| `"MACD.DIFF"(n1,n2,n3)` | | | DIF 线 |
| `"MACD.DEA"(n1,n2,n3)` | | | DEA 线 |
| `"KDJ.K"(n,3,3)` | | KDJ 标准 | K 线 |
| `"KDJ.D"(n,3,3)` | | | D 线 |
| `"KDJ.J"(n,3,3)` | | | J 线 |
| `"W&R"(n)` | | W&R 标准 | 威廉指标 |
| `"RSI.RSI1"(n,?,24)` | | | RSI |
| `HLTHBQ(C,1,1,1)` | 双线穿越 | HLT 双线穿越 | 红白圈买/卖点 |
| `HLTDMISTATIC(n,k)` | n 周期, k 线 | HLT DMI 静态 | +DI/-DI |
| `ISDEPART(x,dir,m)` | dir=1 顶 / 2 底 | 背离判定 | 背离信号 |

---

## D. 复合买点门控（SIGNAL_LOGIC.md 公式原文）

```c
// 最终信号 = 6 大类 AND
: EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT
  AND PRICERESULT AND MOREKLINERESULT AND HLSIGNALRESULT , 0, RGB(255,255,0);

// 6 组在 EXE 常量里全部恒真（实际约束由原子条件 OR 聚合决定）
EMARESULT       := 1;
PROBABILILYRESULT := 1;   // 注: 源码拼写 PROBABILILY
ENERGYRESULT    := 1;
PRICERESULT     := 1;
MOREKLINERESULT := 1;
HLSIGNALRESULT  := 1;
```

---

## E. 原子条件伪代码（节选，对照 TV）

```c
// ---- KDJ 信号 (SIGNAL1..4RESULT) ----
RSV     = (CLOSE - LLV(LOW,9))  / (HHV(HIGH,9) - LLV(LOW,9)) * 100;   // spj_rsv
K       = SMA(RSV, 3, 1);     // spj_k
D       = SMA(K,   3, 1);     // spj_d
J       = 3*K - 2*D;          // spj_j
SIGNAL1RESULT = (REF(J,1) <= 50) AND (J > 50);     // J 上穿 50 → 买
SIGNAL2RESULT = (REF(J,1) >  50) AND (J > 50);     // J 在 50 上方
SIGNAL3RESULT = (REF(J,1) >  50) AND (J <= 50);    // J 下穿 50
SIGNAL4RESULT = (REF(J,1) <= 50) AND (J <= 50);    // J 在 50 下方

// ---- 通道 + KDJ + MACD 综合 (ZHSIGNAL1..10RESULT) ----
ZHSIGNAL1 = MA(HIGH,30) * 1.15;   // 通道上轨
ZHSIGNAL2 = MA(HIGH, 8)  * 1.03;
ZHSIGNAL3 = MA(LOW,  8)  * 0.97;   // 通道下轨
ZHSIGNAL4 = MA(LOW,  30) * 0.85;
ZHSIGNAL1RESULT = (REF(ZHSIGNAL4,1) > REF(ZHSIGNAL3,1)) AND (ZHSIGNAL4 <= ZHSIGNAL3);  // 下轨上穿
ZHSIGNAL5 = RSV(9);
ZHSIGNAL6 = SMA(ZHSIGNAL5, 3, 1);
ZHSIGNAL7 = SMA(ZHSIGNAL6, 3, 1);
ZHSIGNAL9 = EMA(CLOSE,12) - EMA(CLOSE,26);     // MACD 快线差
ZHSIGNAL10 = EMA(ZHSIGNAL9, 9);                // MACD 信号线
ZHSIGNAL2RESULT = (ZHSIGNAL6 > ZHSIGNAL7)
               AND (REF(ZHSIGNAL6,1) < REF(ZHSIGNAL7,1))   // KDJ 金叉
               AND (REF(ZHSIGNAL7,1) < ZHSIGNAL7)           // D 上行
               AND (REF(ZHSIGNAL10,1) - REF(ZHSIGNAL9,1)) > (ZHSIGNAL10 - ZHSIGNAL9)  // 红柱放大
               AND (ZHSIGNAL9 < ZHSIGNAL10);

// ---- 红绿信号 (REDGREEN1/2RESULT) ----
READHEAD2 = SMA(MAX(CLOSE - REF(CLOSE,1), 0), 20, 1)
          / SMA(ABS(CLOSE - REF(CLOSE,1)), 20, 1) * 100;   // 20 日 RSI
REDGREEN1RESULT = (READHEAD2 <= 50) AND (REF(READHEAD2,1) > 50);  // RSI 下穿 50
REDGREEN2RESULT = (READHEAD2 >  50) AND (REF(READHEAD2,1) <= 50); // RSI 上穿 50

// ---- 太极信号 (TJ1/2RESULT) ----
TJHEAD2 = SMA(MAX(CLOSE - REF(CLOSE,1), 0), 9, 1)
        / SMA(ABS(CLOSE - REF(CLOSE,1), 9, 1)) * 100;       // 9 日 RSI
TJ1RESULT = (REF(TJHEAD2,1) <= 20) AND (TJHEAD2 > 20);   // RSI(9) 上穿 20（超卖回升）
TJ2RESULT = (REF(TJHEAD2,1) >= 80) AND (TJHEAD2 < 80);   // RSI(9) 下穿 80（超买卖出）

// ---- MACD 绿柱变长 (MA10RESULT, 截图勾选项) ----
MA10MID = "MACD.MACD"(12, 26, 9);
MA10RESULT = (MA10MID > 0) AND (REF(MA10MID,1) < MA10MID);   // 红柱(绿柱)变长

// ---- 3日-6日均线差放大 (MA1RESULT, 截图勾选项) ----
MA1RESULT = (MA(C,3) - MA(C,6)) > REF(MA(C,3) - MA(C,6), 1);

// ---- HLTHBQ 红白圈 (MA22/23RESULT) ----
MA22RESULT = (REF(HLTHBQ(C,1,1,1),1) > REF(C,1)) AND (HLTHBQ(C,1,1,1) < C);  // 白圈转红=买
MA23RESULT = (REF(HLTHBQ(C,1,1,1),1) < REF(C,1)) AND (HLTHBQ(C,1,1,1) > C);  // 红圈转白=卖

// ---- 量能 (VOL2/HAND2RESULT) ----
VOL2RESULT = (VOL > REF(VOL,1)) AND (REF(VOL,1) > REF(VOL,2));   // 量递增
HAND2RESULT = vrValue > lo AND vrValue < hi;   // vrValue = 上涨量占比区间
  // vrValue = SUM(IF(CLOSE>REF(CLOSE,1),VOL,0),N) / SUM(IF(CLOSE<=REF(CLOSE,1),VOL,0),N) * 100
```

> 全部公式源码以**明文**嵌在 EXE `.rdata`（地址见 SIGNAL_LOGIC.md），无加密。上面伪代码与 TV 语法一一对应，可直接逐行照抄验证。
