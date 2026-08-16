# Fortune.exe 选股条件补全（概率类 + 通用原子）

> 校准：之前列的 73 条底层原子公式**不完整**，漏了 EXE `.rdata` 中的 **「概率类」** 整块。
> 注意：**「八大天王」（趋势王/背离王/波段王/操盘王/多空王/箱体王/换手王）不在 Homily Fortune 里**，
> 它在 `预测大师/HLLevel2.EXE`（见独立分析）。本文件只记录 Fortune.exe 真实存在的公式。
>
> 全部为 Fortune.exe `.rdata` 明文常量铁证，非推测。

## 0. Fortune 顶层 UI 分类（黄点门资源串 @ 0x00894bd7 铁证）
`弘历信号集` / `K线组合` / `行情类` / `能量类` / `概率类` / `移动平均成本类`（含 `信号方案`）
> 注：资源串里**没有**「八大天王」——八大天王是预测大师的，不属于 Fortune。

## 1. 黄点最终信号门（铁证 @ 0x00894bd7）
```
:EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT AND PRICERESULT
 AND MOREKLINERESULT AND HLSIGNALRESULT,0,RGB(255,255,0);
```
六大组 AND，全部成立才出黄点预警。

---

## 2. 概率类 PROBABILILYRESULT（铁证 @ 0x008912fc）
`PROBABILILYRESULT:=1` 后接 **19 个原子条件全 AND**：

| 原子 | 指标 | 公式（.rdata 原文） |
|---|---|---|
| KDJ1 | KDJ.K | `KDJ1MID1:="KDJ.K"(%d,3,3);KDJ1RESULT:=KDJ1MID1 > %d AND KDJ1MID1 < %d;` |
| KDJ2 | KDJ.D | `KDJ2MID2:="KDJ.D"(%d,3,3);KDJ2RESULT:=KDJ2MID2 > %d AND KDJ2MID2 < %d;` |
| KDJ3 | KDJ.J | `KDJ3MID3:="KDJ.J"(%d,3,3);KDJ3RESULT:=KDJ3MID3 > %d AND KDJ3MID3 < %d;` |
| KDJ4 | KDJ.K 顶背离 | `KDJ4MID1:="KDJ.K"(%d,3,3);KDJ4RESULT:=ISDEPART(KDJ4MID1,1,%d);` |
| KDJ5 | KDJ.K 底背离 | `KDJ5MID1:="KDJ.K"(%d,3,3);KDJ5RESULT:=ISDEPART(KDJ5MID1,2,%d);` |
| KDJ6 | KDJ 死叉 | `KDJ6MID1:="KDJ.K"(%d,3,3);KDJ6MID2:="KDJ.D"(%d,3,3);KDJ6RESULT:=KDJ6MID1 > KDJ6MID2 AND REF(KDJ6MID1,1) < REF(KDJ6MID2,1) AND KDJ6MID2 > REF(KDJ6MID2,1);` |
| KDJ7 | KDJ 金叉 | `KDJ7MID1:="KDJ.K"(%d,3,3);KDJ7MID2:="KDJ.D"(%d,3,3);KDJ7RESULT:=KDJ7MID1 < KDJ7MID2 AND REF(KDJ7MID1,1) > REF(KDJ7MID2,1) AND KDJ7MID2 < REF(KDJ7MID2,1);` |
| DMI1 | DMI 金叉 | `DMI1MID1:=HLTDMISTATIC(%d,1);DMI1MID2:=HLTDMISTATIC(%d,2);DMI1RESULT:=DMI1MID1 > DMI1MID2 AND REF(DMI1MID1,1) < REF(DMI1MID2,1);` |
| DMI2 | DMI 死叉 | `DMI2MID1:=HLTDMISTATIC(%d,1);DMI2MID2:=HLTDMISTATIC(%d,2);DMI2RESULT:=DMI2MID1 < DMI2MID2 AND REF(DMI2MID1,1) > REF(DMI2MID2,1);` |
| WR1 | W&R 区间 | `WR1MID:="W&R"(%d);WR1RESULT:=WR1MID > %d AND WR1MID < %d;` |
| WR2 | W&R 触底计数 | `WR2MID:="W&R"(%d);WR2RESULT:=COUNT(WR2MID>%d,%d)>=%d;` |
| WR3 | W&R 触顶计数 | `WR3MID:="W&R"(%d);WR3RESULT:=COUNT(WR3MID<%d,%d)>=%d;` |
| RSI1 | RSI 区间 | `RSI1MID1:="RSI.RSI1"(%d,%d,24);RSI1RESULT:=RSI1MID1 > %d AND RSI1MID1 < %d;` |
| RSI2 | RSI 顶背离 | `RSI2MID1:="RSI.RSI1"(%d,%d,24);RSI2RESULT:=ISDEPART(RSI2MID1,1,%d);` |
| RSI3 | RSI 底背离 | `RSI3MID1:="RSI.RSI1"(%d,%d,24);RSI3RESULT:=ISDEPART(RSI3MID1,2,%d);` |
| RSI4 | RSI 死叉 | `RSI4MID1:="RSI.RSI1"(%d,%d,24);RSI4MID2:="RSI.RSI2"(%d,%d,24);RSI4RESULT:=RSI4MID1>RSI4MID2 AND REF(RSI4MID1,1) < REF(RSI4MID2,1) AND RSI4MID2 > REF(RSI4MID2,1);` |
| RSI5 | RSI 金叉 | `RSI5MID1:="RSI.RSI1"(%d,%d,24);RSI5MID2:="RSI.RSI2"(%d,%d,24);RSI5RESULT:=RSI5MID1<RSI5MID2 AND REF(RSI5MID1,1) > REF(RSI5MID2,1) AND RSI5MID2 < REF(RSI5MID2,1);` |

> 概率类 = 上述 19 条件 **AND**（非 OR）。
> `HLTDMISTATIC` = 弘历 DMI 静态指标；`ISDEPART` = 背离算子（中源问鼎 dll 实现）。

---

## 3. Fortune 通用信号原子（黄点系统子条件，铁证 @ 0x0088e620 块）
这些原子被黄点门六大组引用（HAND=换手、VOL=量能、MA=均线/MACD/弘历通道、ZHSIGNAL/REDGREEN/TJ/SIGNAL=弘历信号集）。
**注意：它们是 Fortune 黄点系统的通用原子，不是「八大天王」分组**（八大天王在预测大师）。

### 3.1 换手（HAND）
- `HAND1:=VOL / CAPITAL;HAND1RESULT:=HANDIF1 > %f AND HANDIF1 < %f;`
- `vrLC:=REF(CLOSE,1);vrValue:=SUM(IF(CLOSE>vrLC,VOL,0),%d)/SUM(IF(CLOSE<=vrLC,VOL,0),%d)*100;HAND2RESULT:=vrValue > %d AND vrValue < %d;`

### 3.2 量能（VOL1-6）
- `VOL1:=VOL %s REF(VOL,1)*%f;`
- `VOL2:=VOL > REF(VOL,1) AND REF(VOL,1) > REF(VOL,2);`
- `VOL3:=VOL < REF(VOL,1) AND REF(VOL,1) < REF(VOL,2);`
- `VOL4:=MA(VOL,%d) %s MA(VOL,%d);`
- `VOL5:=MA(VOL,%d) %s MA(VOL,%d) AND MA(VOL,%d) %s MA(VOL,%d);`
- `VOL6:=SUM(VOL,%d) %s (SUM(VOL,%d) - SUM(VOL,%d));`

### 3.3 能量类 ENERGYRESULT:=1（组恒真）

### 3.4 移动平均成本（MA1-23，全 AND 门 @ 0x008fa41）
- MA1-6：均线乖离 / 弘历通道 UPPER(10,10)
- MA7-12：MA(C) vs (H+L)/2 乖离计数 / 弘历通道 UPPER
- MA13-16：MACD.DIFF/DEA、MACD.MACD 金叉死叉
- MA17-21：多均线排列
- MA22-23：`HLTHBQ(C,1,1,1)`（弘历进退/双线穿越趋势）
- MABIAS5：收盘价乖离率

### 3.5 弘历信号集 HLSIGNALRESULT:=1（子条件全 AND 门 @ 0x008ec1a）
- ZHSIGNAL1-10（综合信号：MA(HIGH/LOW,8/30) 通道突破）
- REDGREEN1/2（红白圈：READHEAD2 穿越 50）
- TJ1/2（TJHEAD2 穿越 20/80）
- SIGNAL1-4（SIGNALHEAD4 穿越 50）

---

## 4. 原始提取
- 全部原始常量串：`_archive/top_categories_raw.txt`（417 tokens，含未解析 %d 参数）

## 5. 置信度
- **铁证（100% 逆）**：本文件所有公式均来自 Fortune.exe `.rdata` 明文常量，非推测。
- **八大天王不在此文件**：八大天王（趋势王/背离王/波段王/操盘王/多空王/箱体王/换手王）属于 `预测大师/HLLevel2.EXE`，已移除本文件的错误对应，另见独立分析。
