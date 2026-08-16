## 七、公式计算核心逻辑（FormulaBase / FormulaCalc.cpp）— 聚焦反编译坐实

### 7.1 引擎定位（Ghidra 反编译铁证）
- 公式引擎类字符串在 EXE `0x008eb918`：`FormulaCalcl` / `.\FormulaCalc.cpp` / `0x008ec5c0`：`FormulaBase`。
- `0x008eb5c0`–`0x008eee80` 共 **13 个函数** = FormulaBase 的算子实现层（全部含 `do{...iVar8+=0xc; pdVar7+=0xc;}while(...)` 逐记录循环，合计 53 个 while 循环 = 逐 K 线遍历）。
- `0x009167a0` = **公式函数注册表**：把 `NETVALUE/ADVANCE/AMOUNT/CLOSE/COUNT/BARSLAST/HHVBARS/LLVBARS/BACKSET/BARSCOUNT/…` 等内建函数逐个 `FUN_0091dda0(code)` 注册进引擎的词法表（确认引擎自带完整公式函数集，运行时解析执行，非预存）。

### 7.2 逐 K 线求值（核心函数 FUN_008eee80 @ 0x008eee80）
反编译还原的主干逻辑（已剥异常处理壳）：
```c
double* CalcSeries(double* out, int* series, int len, int flag, uint* ok) {
    if (len == 0 || (n = FUN_0090a570()) < 1) { *out = NAN; *ok = 0; return; }   // 无数据→NaN
    int L  = FUN_0090a540();          // 序列长度（bar 数）
    int L2 = FUN_0090a540();
    if (FUN_008e6930(series) == 0 || L==0 || L2==0) { *out = NAN; return; }     // 序列校验
    FUN_0090a5c0();                    // 进入该序列上下文
    fVar9  = (*(code**)(*series + 0xc))();        // 算子: getValueAt(bar i)
    fVar10 = (*(code**)(*series + 0xc))(L2);       // 算子: getValueAt(bar L2)
    dStack = (double)fVar10;
    if (flag==0 || FUN_00909ae0()==0) {
        // ... 初始化/对齐首尾 ...
        int iVar8 = iVar5 * 0xc;       // 每条记录 12 字节 (double)
        double* pd = (double*)(iVar8 + buf);
        int remaining = L - iVar5;
        do {                            // ← 逐 K 线循环
            if (*pd != NAN) {
                // 调算子/取该 bar 值，写入 out 缓冲区 (param_4+0x14)
                *(double*)(*(int*)(param_4+0x14) + iVar8) = value_at_bar;
            }
            iVar8 += 0xc;               // 下一条 K 线
            pd    += 0xc;
        } while (remaining-- != 0);
    }
    ...
}
```
→ **铁证**：引擎对每只股票的 OHLCV 序列，按 bar 下标 `i` 循环调用算子 `getValueAt(i)`，把每个原子条件的结果写回输出数组。这就是"逐 K 线求值"的 C++ 实锤，对应你那套公式里 `REF(X,1)`/`LLV(LOW,9)`/`SMA(...,3,1)` 等全是对"历史 bar"的访问。

### 7.3 与 CompMan-chs.dll 的对接
公式里 `"MACD.MACD"(n1,n2,n3)` / `"KDJ.K"(n,3,3)` / `HLTHBQ(C,1,1,1)` / `HLTDMISTATIC(n,k)` / `ISDEPART(x,dir,m)` 这些**算子名**，正是引擎在 `FUN_009167a0` 注册表里注册的外部函数——运行时由 `CompMan-chs.dll` 提供实现（即之前逆的 HLT 算子族）。EXE 自身不含这些算法的数学，只做"公式解析 + 逐 bar 调度 + 结果 AND 门"。

### 7.4 计算路径闭环（回答你最初两个问题）
```
本地 .day/.fen (原始OHLCV)
   │  （无预存信号库，HelpID明文"This analysis is based on local candlestick data"）
   ▼
条件选股：对"股票范围"内每只股 ──for(stock)──┐
   │                                          │
   ▼                                          │
FormulaBase 引擎：FUN_009167a0 注册函数表     │
   │  FUN_008eee80 逐 K 线循环求值每个 *RESULT │
   ▼                                          │
AND 门：EMARESULT AND … HLSIGNALRESULT        │
   │  (= 用户勾选条件 OR-聚合后，6 组全真)      │
   ▼                                          │
命中 → 结果列表 / 图上黄点 ────────────────────┘
                  （选股：全历史重算；预警：只对新 bar 增量算）
```
- **改 filter → 重算**：选股模式下 `for(stock)` 每次重新跑引擎（无结果缓存，已铁证：磁盘无信号库 + 引擎逐 bar 现算）。
- **预警**：同一引擎，但只对新到达的 bar 调 `FUN_008eee80`（增量），不重跑全历史（由 `预警时间间隔` 轮询 + RecvSend 主推 + `没运行预警/预警计算发生异常` 字符串逻辑推出，高置信）。

### 7.5 置信度分层
- **铁证（反编译）**：公式引擎 `0x008eb5c0–0x008eee80` 逐 K 线循环；`FUN_009167a0` 函数注册表；`FUN_008eee80` 的 `do{...+=0xc}while` 逐 bar 写结果；公式算子名（`MACD.MACD`/`HLTHBQ`/…）与 `CompMan-chs.dll` HLT 族对应。
- **高置信推论**：选股=`for(stock)` 全重算、预警=增量（由铁证 + 无信号库文件 + `预警时间间隔` 轮询参数推出）。
- **未坐实**：`for(stock)` 外层循环的确切 C++ 函数（被虚调用/启动期函数指针表动态调用，Ghidra 静态 xref 未捕获；`FUN_009167a0` 与其调用者均无静态 CALL 引用）。如需 100% 钉死该外层循环，需对"选股执行"按钮的 `OnOK`/命令分发做运行时跟踪或聚焦反编译 `0x0088ea00` 信号对话框的命令 handler。
