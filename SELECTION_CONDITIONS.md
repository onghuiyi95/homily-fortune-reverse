# 弘历 Fortune.EXE — 40+ 选股条件完整清单与选股逻辑

> 全部公式源码以**明文**嵌在 EXE `.rdata`（地址见各条），无加密。参数 `%d`/`%f` 为 UI 可填项。
> 算子说明：`"MACD.MACD"`/`"KDJ.K"`/`HLTHBQ`/`HLTDMISTATIC`/`ISDEPART` 由 `CompMan-chs.dll` 提供实现。

---

## 选股逻辑总览（先看这个）

1. **6 大类 AND 门控**：最终买点 = `EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT AND PRICERESULT AND MOREKLINERESULT AND HLSIGNALRESULT`（@ `0x00894bc8`，黄点 `RGB(255,255,0)`）。
2. **6 个大类在 EXE 常量里全部 `:=1`（恒真）**——真正的过滤由 40+ 个**原子条件**决定。
3. **⚠️ 组内 = AND（二进制铁证，2026-08-16）**：在某一大类标签内勾选的多个原子条件，**必须全部同时满足**该类才放行（不是 OR）。即"勾选 = 收紧过滤"。6 大类之间也是 AND → **所有勾选的原子条件同时为真才出买点**。

   **铁证（EXE `.rdata` 模板原文，非推断）**：每组都是一条用 `AND` 固定串联的模板链，组尾是该组恒真默认 `:=1`：
   ```
   ... AND MA11RESULT AND MA10RESULT ... AND MA1RESULT        EMARESULT:=1
   ... AND CLOSE11RESULT ... AND CLOSE1RESULT AND MARKETVALUERESULT   PRICERESULT:=1
   ... AND KDJ7RESULT ... AND KDJ1RESULT AND DMI2RESULT ... AND RSI1RESULT   PROBABILILYRESULT:=1
   ... AND VOL6RESULT ... AND VOL1RESULT                      ENERGYRESULT:=1
   ```
   C++ 勾选条件 N 时，仅把对应的 `XRESULT:=1` 替换为 `XRESULT:=<真实公式>`；未勾选保持 `:=1`（恒真）。因整条链是 `AND`，勾选的必须为真、未勾选的恒真 → **所有勾选条件必同时为真 = 组内 AND**。这推翻了早期误写的 OR（无据猜测），已更正。
4. **无勾选 = 该类恒真**（放行，因 EXE 里各组 `:=1` 默认真，C++ 只在勾选时插入约束）。
5. **逐股现算**：对股票范围内每只股，引擎（`FormulaBase`/`FUN_008eee80`）逐 K 线求值每个原子条件，末尾做 AND 门判定。改 filter → 全重算（无结果缓存）。

---

## A. MA 组（EMARESULT，地址 `0x0088fc0c` 恒真；原子 MA1–MA23）

| # | 原子 | 公式（EXE 地址） | 含义 |
|---|---|---|---|
| 1 | `MA1RESULT` | `MA(C,a)-MA(C,b) %s REF(MA(C,a)-MA(C,b),1)` (`0x008905bc`) | 两均线差放大/缩小（截图勾选项：3日-6日） |
| 2 | `MA2RESULT` | `MA1>MA2 AND REF(MA1,1)<REF(MA2,1) AND MA2>REF(MA2,1)` (`0x00890520`) | 短均上穿长均（金叉）且长均上行 |
| 3 | `MA3RESULT` | `MA1<MA2 AND REF(MA1,1)>REF(MA2,1) AND MA2<REF(MA2,1)` (`0x00890480`) | 短均下穿长均（死叉）且长均下行 |
| 4 | `MA4RESULT` | `MABIAS=(C-MA(C,n))/MA(C,n)*100; MABIAS>%d AND <%d` (`0x00890418`) | 均线乖离率在区间 |
| 5 | `MA5RESULT` | `MABIAS %s REF(MABIAS,1)` (`0x008903b0`) | 乖离率放大/缩小 |
| 6 | `MA6RESULT` | `"BOLL.UPPER"(10,10) < C AND !=0` (`0x00890358`) | 收盘在布林上轨下方 |
| 7 | `MA7RESULT` | `MA(C,n);mid=(H+L)/2; COUNT(ABS(MA-mid)/mid<=%,N)==%d` (`0x00890288`) | 收盘价贴近均价（通道窄）次数达标 |
| 8 | `MA8RESULT` | `DIFF>DEA AND REF(DIFF,1)<REF(DEA,1) AND DEA>REF(DEA,1)` (`0x008901d0`) | MACD 金叉（DIFF 上穿 DEA） |
| 9 | `MA9RESULT` | `"MACD.MACD">0 AND REF(.,1)<0` (`0x00890178`) | MACD 上穿 0 轴 |
| 10 | `MA10RESULT` | `"MACD.MACD">0 AND REF(.,1)<MACD` (`0x00890110`) | MACD 红柱变长（截图勾选项） |
| 11 | `MA11RESULT` | `"MACD.MACD"<0 AND REF(.,1)>MACD` (`0x008900a8`) | MACD 绿柱变长 |
| 12 | `MA12RESULT` | `"BOLL.UPPER"(10,10) > C AND !=0` (`0x00890300`) | 收盘在布林上轨上方 |
| 13 | `MA13RESULT` | `DIFF<DEA AND REF(DIFF,1)>REF(DEA,1) AND DEA<REF(DEA,1)` (`0x0088ffe8`) | MACD 死叉 |
| 14 | `MA14RESULT` | `"MACD.MACD"<0 AND REF(.,1)>0` (`0x0088ff88`) | MACD 下穿 0 轴 |
| 15 | `MA15RESULT` | `"MACD.MACD">0 AND REF(.,1)>MACD` (`0x008ff20`) | MACD 红柱缩短 |
| 16 | `MA16RESULT` | `"MACD.MACD"<0 AND REF(.,1)<MACD` (`0x008feb8`) | MACD 绿柱缩短 |
| 17 | `MA17RESULT` | `MA(C,n) %s MA(C,m)`（双均关系）(`0x008fe70`) | 两均线多空排列 |
| 18 | `MA18RESULT` | `MA(C,n) %s MA(C,m)` (`0x008fe28`) | 两均线关系（另一组） |
| 19 | `MA19RESULT` | `MA(C,n) %s MA(C,m) AND MA(C,m) %s MA(C,k)` (`0x008fde0`) | 三均线多头/空头排列 |
| 20 | `MA20RESULT` | `MA(C,n); COUNT(MA %s REF(MA,1),N)==%d AND C %s MA` (`0x008fd70`) | 均线连涨 N 日且价在线上 |
| 21 | `MA21RESULT` | `MA(C,n); mid=(H+L)/2; COUNT(ABS(MA-mid)/mid<=%f,N)==%d AND C %s MA` (`0x008fce0`) | 收盘贴近均价 N 日且价在线上 |
| 22 | `MA22RESULT` | `HLTHBQ(C,1,1,1); REF(MID,1)>REF(C,1) AND MID<C` (`0x008fc80`) | 红白圈：白圈转红 = **买点** |
| 23 | `MA23RESULT` | `HLTHBQ(C,1,1,1); REF(MID,1)<REF(C,1) AND MID>C` (`0x008fc20`) | 红白圈：红圈转白 = **卖点** |

---

## B. Probability 组（PROBABILILYRESULT，地址 `0x008912fc` 恒真）

**0 个原子条件**——纯占位（源码拼写错别字 `PROBABILILY`）。恒真放行。

---

## C. Energy 组（ENERGYRESULT，地址 `0x0088e708` 恒真；原子 HAND1/2 + VOL1–6）

| # | 原子 | 公式（EXE 地址） | 含义 |
|---|---|---|---|
| 24 | `HAND1RESULT` | `HANDIF1=VOL/CAPITAL; HANDIF1>%f AND <%f` (`0x0088e7c8`) | 换手率在区间 |
| 25 | `HAND2RESULT` | `vrLC=REF(C,1); vrValue=SUM(IF(C>vrLC,VOL,0),N)/SUM(IF(C<=vrLC,VOL,0),N)*100; vrValue>%d AND <%d` (`0x0088e720`) | 量比（上涨量/下跌量占比）区间 |
| 26 | `VOL1RESULT` | `VOL %s REF(VOL,1)*%f` (`0x0088e97c`) | 量能放/缩倍 |
| 27 | `VOL2RESULT` | `VOL>REF(VOL,1) AND REF(VOL,1)>REF(VOL,2)` (`0x0088e934`) | 量递增（截图勾选项） |
| 28 | `VOL3RESULT` | `VOL<REF(VOL,1) AND REF(VOL,1)<REF(VOL,2)` (`0x0088e8ec`) | 量递减 |
| 29 | `VOL4RESULT` | `MA(VOL,n) %s MA(VOL,m)` (`0x0088e8bc`) | 量均线关系 |
| 30 | `VOL5RESULT` | `MA(VOL,n) %s MA(VOL,m) AND MA(VOL,m) %s MA(VOL,k)` (`0x0088e868`) | 量均线多/空排列 |
| 31 | `VOL6RESULT` | `SUM(VOL,n) %s (SUM(VOL,n)-SUM(VOL,m))` (`0x0088e81c`) | 阶段累计量比较 |

---

## D. Quotation 组（PRICERESULT，地址 `0x00890a24` 恒真；原子 CLOSE1–14 + MARKETVALUE）

| # | 原子 | 公式（EXE 地址） | 含义 |
|---|---|---|---|
| 32 | `CLOSE1RESULT` | `(C-REF(C,1))/REF(C,1)*100 > %d AND <%d` (`0x00890df0`) | 涨幅在区间 |
| 33 | `CLOSE2RESULT` | `LJZHANGFU=100*(C-REF(C,n))/REF(C,n); >%d AND <%d` (`0x00890d80`) | N 日累计涨幅区间 |
| 34 | `CLOSE3RESULT` | `C==H` (`0x00890d68`) | 收在最高（光头） |
| 35 | `CLOSE4RESULT` | `C>HHV(REF(C,1),DATACOUNT-1)` (`0x00890d18`) | 创历史/区间新高 |
| 36 | `CLOSE5RESULT` | `C==L` (`0x00890d00`) | 收在最低（光脚） |
| 37 | `CLOSE6RESULT` | `C<LLV(REF(C,1),DATACOUNT-1)` (`0x00890cb0`) | 创历史/区间新低 |
| 38 | `CLOSE7RESULT` | `UPSPACEPRICE:=L>REF(H,1); SUM(.,N)>=%d` (`0x00890c58`) | N 日向上跳空次数 |
| 39 | `CLOSE8RESULT` | `DOWNSPACEPRICE:=H<REF(L,1); SUM(.,N)>=%d` (`0x00890c00`) | N 日向下跳空次数 |
| 40 | `CLOSE9RESULT` | `QJZHENFU=(HHV(H,n)-LLV(L,n))/LLV(L,n)*100; >%d AND <%d` (`0x00890b88`) | 区间振幅在区间 |
| 41 | `CLOSE10RESULT` | `SUM(涨幅>=0,N)==%d` (`0x00890b20`) | N 日连涨天数达标 |
| 42 | `CLOSE11RESULT` | `SUM(涨幅<=0,N)==%d` (`0x00890ab8`) | N 日连跌天数达标 |
| 43 | `CLOSE12RESULT` | `C>=HHV(REF(C,1),n)` (`0x00890a8c`) | 创 N 日新高 |
| 44 | `CLOSE13RESULT` | `C<=LLV(REF(C,1),n)` (`0x00890a60`) | 创 N 日新低 |
| 45 | `CLOSE14RESULT` | `C>%d AND C<%d` (`0x00890a38`) | 收盘价绝对区间 |
| 46 | `MARKETVALUERESULT` | `MARKETVALUE=CAPITAL*C; >%d AND <%d` (`0x00890e68`) | 总市值在区间 |

---

## E. Candlestick Pattern 组（MOREKLINERESULT，地址 `0x0088f6ec` 恒真）

**复合公式里该组恒真**。但信号对话框「Candlestick Pattern」标签实际承载的是 **KDJ / RSI / W&R / DMI** 系列（见 F 组原子在 UI 归到该标签下，EXE 字符串 `0x008911a8`–`0x008912e8` 紧接 `HLSIGNALRESULT` 之前）。即"更多 K 线形态"= KDJ/RSI/WR/DMI 子类。

---

## F. Homily Signals 组（HLSIGNALRESULT，地址 `0x0088ed04` 恒真；原子 SIGNAL/KDJ/RSI/WR/DMI/ZHSIGNAL/REDGREEN/TJ）

| # | 原子 | 公式（EXE 地址） | 含义 |
|---|---|---|---|
| 47 | `SIGNAL1RESULT` | `J 上穿 50` (`0x008f31c`) | KDJ-J 买 |
| 48 | `SIGNAL2RESULT` | `J 在 50 上方` (`0x008f2d0`) | |
| 49 | `SIGNAL3RESULT` | `J 下穿 50` (`0x008f284`) | KDJ-J 卖 |
| 50 | `SIGNAL4RESULT` | `J 在 50 下方` (`0x008f238`) | |
| 51 | `KDJ1RESULT` | `KDJ.K 在区间` (`0x008915d0`) | |
| 52 | `KDJ2RESULT` | `KDJ.D 在区间` (`0x00891578`) | |
| 53 | `KDJ3RESULT` | `KDJ.J 在区间` (`0x00891520`) | |
| 54 | `KDJ4RESULT` | `ISDEPART(KDJ.K, 1, m)` 顶背离 (`0x008914d4`) | |
| 55 | `KDJ5RESULT` | `ISDEPART(KDJ.K, 2, m)` 底背离 (`0x00891488`) | |
| 56 | `KDJ6RESULT` | `K 上穿 D 且 D 上行`（金叉）(`0x008913d0`) | |
| 57 | `KDJ7RESULT` | `K 下穿 D 且 D 下行`（死叉）(`0x00891318`) | |
| 58 | `RSI1RESULT` | `RSI1 在区间` (`0x00891a70`) | |
| 59 | `RSI2RESULT` | `ISDEPART(RSI1,1,m)` 顶背离 (`0x00891a18`) | |
| 60 | `RSI3RESULT` | `ISDEPART(RSI1,2,m)` 底背离 (`0x008919c0`) | |
| 61 | `RSI4RESULT` | `RSI1 上穿 RSI2`（金叉）(`0x008918f8`) | |
| 62 | `RSI5RESULT` | `RSI1 下穿 RSI2`（死叉）(`0x00891830`) | |
| 63 | `WR1RESULT` | `W&R 在区间` (`0x008917e4`) | |
| 64 | `WR2RESULT` | `COUNT(WR>%d,N)>=%d` (`0x008917a4`) | N 日 W&R 高位天数 |
| 65 | `WR3RESULT` | `COUNT(WR<%d,N)>=%d` (`0x00891764`) | N 日 W&R 低位天数 |
| 66 | `DMI1RESULT` | `+DI 上穿 -DI`（`HLTDMISTATIC` 静态）(`0x00891628`) | |
| 67 | `DMI2RESULT` | `+DI 下穿 -DI` (`0x008916c8`) | |
| 68 | `ZHSIGNAL1RESULT` | 通道下轨上穿（`MA30*0.85` vs `MA8*0.97`）(`0x0088ef48`) | 弘历通道买 |
| 69 | `ZHSIGNAL2RESULT` | 通道+KDJ金叉+MACD红柱放大 (`0x0088ed20`) | 综合买（截图无，属 Homily 信号） |
| 70 | `REDGREEN1RESULT` | 20日RSI 下穿 50 (`0x008f078`) | 红绿信号卖 |
| 71 | `REDGREEN2RESULT` | 20日RSI 上穿 50 (`0x008f030`) | 红绿信号买 |
| 72 | `TJ1RESULT` | 9日RSI 上穿 20（超卖回升）(`0x008f180`) | 太极买 |
| 73 | `TJ2RESULT` | 9日RSI 下穿 80（超买卖出）(`0x008f13c`) | 太极卖 |

> 另有对话框顶层 4 个宏信号（字符串 `0x00879120` 段）：`RED & GREEN SIGNAL` / `TAI CHI SIGNAL` / `BOTTOM CATCH SIGNAL` / `STRONG SIGNAL`——它们是上述原子的命名组合预设。

---

## 选股逻辑伪代码（给用户理解 AND/AND）

```python
# 每个大类 = 组内勾选条件 AND（用户确认: 勾选=收紧, 全部满足才过该类）
def group_pass(group, checked):
    if not checked: return True          # 未勾选 = 恒真放行
    return all(atom(stock) for atom in checked)   # 组内 AND

# 最终买点 = 6 大类 AND
buy_signal = (group_pass("MA",       checked_ma)
          and group_pass("Probability", checked_prob)   # 恒真
          and group_pass("Energy",    checked_energy)
          and group_pass("Quotation", checked_price)
          and group_pass("Candle",    checked_candle)   # 恒真
          and group_pass("Homily",    checked_homily))

# 范围: 板块/自选/全部 → for stock in range: if buy_signal(stock): results.append(stock)
```

**关键语义**：勾选 = 收紧过滤。在某组勾 N 条 → 必须 N 条同时为真该类才放行；6 类全放行才出买点。想放宽就少勾，想严就多勾（与"OR 越勾越松"相反）。

---

## 置信度
- **铁证**：73 个原子条件公式全部来自 EXE `.rdata` 明文常量（地址见上）；6 组 `:=1` 硬编码；复合 AND 门 `0x00894bc8`；**组内 AND 由 `.rdata` 模板的 `AND XRESULT...` 固定串联链证实**（勾选=把 `:=1` 替换为真实公式，未勾=恒真）。
- **未坐实**：`for(stock)` 外层循环精确 C++ 函数（被启动期函数指针动态调用，静态 xref 未捕获）。
