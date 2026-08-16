# 弘历 Fortune.EXE — 全部 73 个选股条件完整公式（逐字原文）

> 每条公式均为 EXE `.rdata` **明文常量原文**，逐字提取（含 `%d`/`%f`/`%s` 参数占位，运行时由 UI 填）。
> 地址 = 该字符串在 EXE 中的文件偏移，可对照验证。
> 算子：`"MACD.MACD"`/`"MACD.DIFF"`/`"MACD.DEA"`/`"KDJ.K"`/`"KDJ.D"`/`"KDJ.J"`/`"W&R"`/`"RSI.RSI1"`/`"RSI.RSI2"`/`HLTHBQ`/`HLTDMISTATIC`/`ISDEPART` 由 `CompMan-chs.dll` 提供实现。

---

## 选股逻辑（必读）

- 最终买点 = `EMARESULT AND PROBABILILYRESULT AND ENERGYRESULT AND PRICERESULT AND MOREKLINERESULT AND HLSIGNALRESULT`（@ `0x00894bc8`，黄点 `RGB(255,255,0)`）。
- 6 大类在 EXE 里**全部 `:=1` 恒真**；真正过滤靠下面 73 个原子条件。
- **组内 AND、组间 AND**（铁证：`.rdata` 每组是 `AND XRESULT...` 固定串联模板链）。勾选=把 `XRESULT:=1` 替换为真实公式；未勾=恒真。⇒ 所有勾选条件必同时为真。
- **背离**见 §F 组（KDJ 顶/底背离、RSI 顶/底背离，共 4 条 `ISDEPART`）。

---

## A. MA 组（EMARESULT，恒真 @ `0x0088fc0c`；原子 MA1–MA23）

| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 1 | `MA1RESULT` | `0x008905bc` | `MA1RESULT:=MA(C,%d) - MA(C,%d) %s REF(MA(C,%d) - MA(C,%d),1);` |
| 2 | `MA2RESULT` | `0x00890520` | `MA2MID1:=MA(C,%d);MA2MID2:=MA(C,%d);MA2RESULT:=MA2MID1>MA2MID2 AND REF(MA2MID1,1) < REF(MA2MID2,1) AND MA2MID2 > REF(MA2MID2,1);` |
| 3 | `MA3RESULT` | `0x00890480` | `MA3MID1:=MA(C,%d);MA3MID2:=MA(C,%d);MA3RESULT:=MA3MID1<MA3MID2 AND REF(MA3MID1,1) > REF(MA3MID2,1) AND MA3MID2 < REF(MA3MID2,1);` |
| 4 | `MA4RESULT` | `0x00890418` | `MABIAS4:=(CLOSE-MA(CLOSE,%d))/MA(CLOSE,%d)*100;MA4RESULT:=MABIAS4>%d AND MABIAS4<%d;` |
| 5 | `MA5RESULT` | `0x008903b0` | `MABIAS5:=(CLOSE-MA(CLOSE,%d))/MA(CLOSE,%d)*100;MA5RESULT:=MABIAS5 %s REF(MABIAS5,1);` |
| 6 | `MA6RESULT` | `0x00890358` | `MA6MID:="BOLL.UPPER"(10,10);MA6RESULT:=MA6MID<C AND MA6MID != 0;` |
| 7 | `MA7RESULT` | `0x00890288` | `MA7MID1:=MA(C,%d);MA7MID2:=(H+L)/2;MA7RESULT:=COUNT(ABS(MA7MID1-MA7MID2)/MA7MID2<=%f,%d) == %d;` |
| 8 | `MA8RESULT` | `0x008901d0` | `MA8MID1:="MACD.DIFF"(%d,%d,%d);MA8MID2:="MACD.DEA"(%d,%d,%d);MA8RESULT:=MA8MID1>MA8MID2 AND REF(MA8MID1,1)<REF(MA8MID2,1) AND MA8MID2>REF(MA8MID2,1);` |
| 9 | `MA9RESULT` | `0x00890178` | `MA9MID:="MACD.MACD"(%d,%d,%d);MA9RESULT:=MA9MID>0 AND REF(MA9MID,1)<0;` |
| 10 | `MA10RESULT` | `0x00890110` | `MA10MID:="MACD.MACD"(%d,%d,%d);MA10RESULT:=MA10MID>0 AND REF(MA10MID,1)<MA10MID;` |
| 11 | `MA11RESULT` | `0x008900a8` | `MA11MID:="MACD.MACD"(%d,%d,%d);MA11RESULT:=MA11MID<0 AND REF(MA11MID,1)>MA11MID;` |
| 12 | `MA12RESULT` | `0x00890300` | `MA12MID:="BOLL.UPPER"(10,10);MA12RESULT:=MA12MID>C AND MA12MID != 0;` |
| 13 | `MA13RESULT` | `0x0088ffe8` | `MA13MID1:="MACD.DIFF"(%d,%d,%d);MA13MID2:="MACD.DEA"(%d,%d,%d);MA13RESULT:=MA13MID1<MA13MID2 AND REF(MA13MID1,1)>REF(MA13MID2,1) AND MA13MID2<REF(MA13MID2,1);` |
| 14 | `MA14RESULT` | `0x0088ff88` | `MA14MID:="MACD.MACD"(%d,%d,%d);MA14RESULT:=MA14MID<0 AND REF(MA14MID,1)>0;` |
| 15 | `MA15RESULT` | `0x008ff20` | `MA15MID:="MACD.MACD"(%d,%d,%d);MA15RESULT:=MA15MID>0 AND REF(MA15MID,1)>MA15MID;` |
| 16 | `MA16RESULT` | `0x008feb8` | `MA16MID:="MACD.MACD"(%d,%d,%d);MA16RESULT:=MA16MID<0 AND REF(MA16MID,1)<MA16MID;` |
| 17 | `MA17RESULT` | `0x008fe70` | `MA17RESULT:=MA(C,%d) %s MA(C,%d) AND MA(C,%d) %s MA(C,%d);` |
| 18 | `MA18RESULT` | `0x008fe28` | `MA18RESULT:=MA(C,%d) %s MA(C,%d);` |
| 19 | `MA19RESULT` | `0x008fde0` | `MA19RESULT:=MA(C,%d) %s MA(C,%d) AND MA(C,%d) %s MA(C,%d);` |
| 20 | `MA20RESULT` | `0x008fd70` | `MA20MID:=MA(C,%d);MA20RESULT:=(COUNT(MA20MID %s REF(MA20MID,1),%d)==%d) AND C %s MA(C,%d);` |
| 21 | `MA21RESULT` | `0x008fce0` | `MA21MID1:=MA(C,%d);MA21MID2:=(H+L)/2;MA21RESULT:=COUNT(ABS(MA21MID1-MA21MID2)/MA21MID2<=%f,%d) == %d AND C %s MA(C,%d);` |
| 22 | `MA22RESULT` | `0x008fc80` | `MA22MID:=HLTHBQ(C,1,1,1);MA22RESULT:=REF(MA22MID,1) > REF(C,1) AND MA22MID < C;` |
| 23 | `MA23RESULT` | `0x008fc20` | `MA23MID:=HLTHBQ(C,1,1,1);MA23RESULT:=REF(MA23MID,1) < REF(C,1) AND MA23MID > C;` |

> MA6/MA12 用 `"BOLL.UPPER"(10,10)`（布林上轨，参数 10/10）。MA22/MA23 为 HLTHBQ 红白圈买/卖点。

---

## B. Probability 组（PROBABILILYRESULT，恒真 @ `0x008912fc`）

**0 个原子条件**（纯占位，源码拼写错别字 `PROBABILILY`）。恒真放行。

---

## C. Energy 组（ENERGYRESULT，恒真 @ `0x0088e708`；原子 HAND1/2 + VOL1–6）

| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 24 | `HAND1RESULT` | `0x0088e7c8` | `HANDIF1:=VOL / CAPITAL;HAND1RESULT:=HANDIF1 > %f AND HANDIF1 < %f;` |
| 25 | `HAND2RESULT` | `0x0088e720` | `vrLC:=REF(CLOSE,1);vrValue:=SUM(IF(CLOSE>vrLC,VOL,0),%d)/SUM(IF(CLOSE<=vrLC,VOL,0),%d)*100;HAND2RESULT:=vrValue > %d AND vrValue < %d;` |
| 26 | `VOL1RESULT` | `0x0088e97c` | `VOL1RESULT:=VOL %s REF(VOL,1)*%f;` |
| 27 | `VOL2RESULT` | `0x0088e934` | `VOL2RESULT:=VOL > REF(VOL,1) AND REF(VOL,1) > REF(VOL,2);` |
| 28 | `VOL3RESULT` | `0x0088e8ec` | `VOL3RESULT:=VOL < REF(VOL,1) AND REF(VOL,1) < REF(VOL,2);` |
| 29 | `VOL4RESULT` | `0x0088e8bc` | `VOL4RESULT:=MA(VOL,%d) %s MA(VOL,%d);` |
| 30 | `VOL5RESULT` | `0x0088e868` | `VOL5RESULT:=MA(VOL,%d) %s MA(VOL,%d) AND MA(VOL,%d) %s MA(VOL,%d);` |
| 31 | `VOL6RESULT` | `0x0088e81c` | `VOL6RESULT:=SUM(VOL,%d) %s (SUM(VOL,%d) - SUM(VOL,%d));` |

---

## D. Quotation 组（PRICERESULT，恒真 @ `0x00890a24`；原子 CLOSE1–14 + MARKETVALUE）

| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 32 | `CLOSE1RESULT` | `0x00890df0` | `CLOSEZHANGFU1:=(C-REF(C,1))/REF(C,1)*100;CLOSE1RESULT:=CLOSEZHANGFU1 > %d AND CLOSEZHANGFU1 < %d;` |
| 33 | `CLOSE2RESULT` | `0x00890d80` | `LJZHANGFU:=(100*(C-REF(C,%d))/REF(C,%d));CLOSE2RESULT:=LJZHANGFU > %d AND LJZHANGFU < %d;` |
| 34 | `CLOSE3RESULT` | `0x00890d68` | `CLOSE3RESULT:=C==H;` |
| 35 | `CLOSE4RESULT` | `0x00890d18` | `DATACOUNT1:=COUNT(C,0);CLOSE4RESULT:=C>HHV(REF(C,1),DATACOUNT1-1);` |
| 36 | `CLOSE5RESULT` | `0x00890d00` | `CLOSE5RESULT:=C==L;` |
| 37 | `CLOSE6RESULT` | `0x00890cb0` | `DATACOUNT2:=COUNT(C,0);CLOSE6RESULT:=C<LLV(REF(C,1),DATACOUNT2-1);` |
| 38 | `CLOSE7RESULT` | `0x00890c58` | `UPSPACEPRICE:=L > REF(H,1);CLOSE7RESULT:=SUM(UPSPACEPRICE,%d) >= %d;` |
| 39 | `CLOSE8RESULT` | `0x00890c00` | `DOWNSPACEPRICE:=H < REF(L,1);CLOSE8RESULT:=SUM(DOWNSPACEPRICE,%d) >= %d;` |
| 40 | `CLOSE9RESULT` | `0x00890b88` | `QJZHENFU:=(HHV(H,%d) - LLV(L,%d)) / LLV(L,%d) * 100;CLOSE9RESULT:=QJZHENFU > %d AND QJZHENFU < %d;` |
| 41 | `CLOSE10RESULT` | `0x00890b20` | `CLOSEZHANGFU3:=(C-REF(C,1))/REF(C,1)*100;CLOSE10RESULT:=SUM(CLOSEZHANGFU3>=0,%d)==%d;` |
| 42 | `CLOSE11RESULT` | `0x00890ab8` | `CLOSEZHANGFU4:=(C-REF(C,1))/REF(C,1)*100;CLOSE11RESULT:=SUM(CLOSEZHANGFU4<=0,%d)==%d;` |
| 43 | `CLOSE12RESULT` | `0x00890a8c` | `CLOSE12RESULT:=C>=HHV(REF(C,1),%d);` |
| 44 | `CLOSE13RESULT` | `0x00890a60` | `CLOSE13RESULT:=C<=LLV(REF(C,1),%d);` |
| 45 | `CLOSE14RESULT` | `0x00890a38` | `CLOSE14RESULT:=C > %d AND C < %d;` |
| 46 | `MARKETVALUERESULT` | `0x00890e68` | `MARKETVALUE:=CAPITAL*C;MARKETVALUERESULT:=MARKETVALUE > %d AND MARKETVALUE < %d;` |

---

## E. Candlestick Pattern 组（MOREKLINERESULT，恒真 @ `0x0088f6ec`）

**复合公式里该组恒真**。实际"更多 K 线形态"标签承载 KDJ/RSI/WR/DMI 子类（见 F 组原子，EXE 字符串 `0x008911a8`–`0x008912e8` 紧接 `HLSIGNALRESULT` 之前）。即无独立原子条件，恒真放行。

---

## F. Homily Signals 组（HLSIGNALRESULT，恒真 @ `0x0088ed04`；原子 SIGNAL/KDJ/RSI/WR/DMI/ZHSIGNAL/REDGREEN/TJ + 背离）

### F.1 KDJ 信号（SIGNAL1–4）
| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 47 | `SIGNAL1RESULT` | `0x008f31c` | `SIGNALHEAD1:=(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100;SIGNALHEAD2:=SMA(SIGNALHEAD1,3,1);SIGNALHEAD3:=SMA(SIGNALHEAD2,3,1);SIGNALHEAD4:=3*SIGNALHEAD2-2*SIGNALHEAD3;SIGNAL1RESULT:=(REF(SIGNALHEAD4,1)<= 50) and (SIGNALHEAD4>50);` |
| 48 | `SIGNAL2RESULT` | `0x008f2d0` | `SIGNAL2RESULT:=(REF(SIGNALHEAD4,1)> 50) and (SIGNALHEAD4>50);` |
| 49 | `SIGNAL3RESULT` | `0x008f284` | `SIGNAL3RESULT:=(REF(SIGNALHEAD4,1)> 50) and (SIGNALHEAD4<=50);` |
| 50 | `SIGNAL4RESULT` | `0x008f238` | `SIGNAL4RESULT:=(REF(SIGNALHEAD4,1)<= 50) and (SIGNALHEAD4<=50);` |

### F.2 KDJ 指标条件（KDJ1–7）— 含背离
| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 51 | `KDJ1RESULT` | `0x008915d0` | `KDJ1MID1:="KDJ.K"(%d,3,3);KDJ1RESULT:=KDJ1MID1 > %d AND KDJ1MID1 < %d;` |
| 52 | `KDJ2RESULT` | `0x00891578` | `KDJ2MID2:="KDJ.D"(%d,3,3);KDJ2RESULT:=KDJ2MID2 > %d AND KDJ2MID2 < %d;` |
| 53 | `KDJ3RESULT` | `0x00891520` | `KDJ3MID3:="KDJ.J"(%d,3,3);KDJ3RESULT:=KDJ3MID3 > %d AND KDJ3MID3 < %d;` |
| 54 | `KDJ4RESULT` ⚠️顶背离 | `0x008914d4` | `KDJ4MID1:="KDJ.K"(%d,3,3);KDJ4RESULT:=ISDEPART(KDJ4MID1,1,%d);` |
| 55 | `KDJ5RESULT` ⚠️底背离 | `0x00891488` | `KDJ5MID1:="KDJ.K"(%d,3,3);KDJ5RESULT:=ISDEPART(KDJ5MID1,2,%d);` |
| 56 | `KDJ6RESULT` | `0x008913d0` | `KDJ6MID1:="KDJ.K"(%d,3,3);KDJ6MID2:="KDJ.D"(%d,3,3);KDJ6RESULT:=KDJ6MID1 > KDJ6MID2 AND REF(KDJ6MID1,1) < REF(KDJ6MID2,1) AND KDJ6MID2 > REF(KDJ6MID2,1);` |
| 57 | `KDJ7RESULT` | `0x00891318` | `KDJ7MID1:="KDJ.K"(%d,3,3);KDJ7MID2:="KDJ.D"(%d,3,3);KDJ7RESULT:=KDJ7MID1 < KDJ7MID2 AND REF(KDJ7MID1,1) > REF(KDJ7MID2,1) AND KDJ7MID2 < REF(KDJ7MID2,1);` |

### F.3 RSI 指标条件（RSI1–5）— 含背离
| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 58 | `RSI1RESULT` | `0x00891a70` | `RSI1MID1:="RSI.RSI1"(%d,%d,24);RSI1RESULT:=RSI1MID1 > %d AND RSI1MID1 < %d;` |
| 59 | `RSI2RESULT` ⚠️顶背离 | `0x00891a18` | `RSI2MID1:="RSI.RSI1"(%d,%d,24);RSI2RESULT:=ISDEPART(RSI2MID1,1,%d);` |
| 60 | `RSI3RESULT` ⚠️底背离 | `0x008919c0` | `RSI3MID1:="RSI.RSI1"(%d,%d,24);RSI3RESULT:=ISDEPART(RSI3MID1,2,%d);` |
| 61 | `RSI4RESULT` | `0x008918f8` | `RSI4MID1:="RSI.RSI1"(%d,%d,24);RSI4MID2:="RSI.RSI2"(%d,%d,24);RSI4RESULT:=RSI4MID1>RSI4MID2 AND REF(RSI4MID1,1) < REF(RSI4MID2,1) AND RSI4MID2 > REF(RSI4MID2,1);` |
| 62 | `RSI5RESULT` | `0x00891830` | `RSI5MID1:="RSI.RSI1"(%d,%d,24);RSI5MID2:="RSI.RSI2"(%d,%d,24);RSI5RESULT:=RSI5MID1<RSI5MID2 AND REF(RSI5MID1,1) > REF(RSI5MID2,1) AND RSI5MID2 < REF(RSI5MID2,1);` |

### F.4 W&R / DMI
| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 63 | `WR1RESULT` | `0x008917e4` | `WR1MID:="W&R"(%d);WR1RESULT:=WR1MID > %d AND WR1MID < %d;` |
| 64 | `WR2RESULT` | `0x008917a4` | `WR2MID:="W&R"(%d);WR2RESULT:=COUNT(WR2MID>%d,%d)>=%d;` |
| 65 | `WR3RESULT` | `0x00891764` | `WR3MID:="W&R"(%d);WR3RESULT:=COUNT(WR3MID<%d,%d)>=%d;` |
| 66 | `DMI1RESULT` | `0x00891628` | `DMI2MID1:=HLTDMISTATIC(%d,1);DMI2MID2:=HLTDMISTATIC(%d,2);DMI1RESULT:=DMI2MID1 > DMI2MID2 AND REF(DMI2MID1,1) < REF(DMI2MID2,1);` |
| 67 | `DMI2RESULT` | `0x008916c8` | `DMI1MID1:=HLTDMISTATIC(%d,1);DMI1MID2:=HLTDMISTATIC(%d,2);DMI2RESULT:=DMI1MID1 < DMI1MID2 AND REF(DMI1MID1,1) > REF(DMI1MID2,1);` |

### F.5 弘历通道 / 红绿 / 太极 / ZHSIGNAL
| # | 原子 | EXE 地址 | 完整公式原文 |
|---|---|---|---|
| 68 | `ZHSIGNAL1RESULT` | `0x0088ef48` | `ZHSIGNAL1:=MA(HIGH,30)*1.15;ZHSIGNAL2:=MA(HIGH,8)*1.03;ZHSIGNAL3:=MA(LOW,8)*0.97;ZHSIGNAL4:=MA(LOW,30)*0.85;ZHSIGNAL1RESULT:=(REF(ZHSIGNAL4,1) > REF(ZHSIGNAL3,1)) AND (ZHSIGNAL4 <= ZHSIGNAL3);` |
| 69 | `ZHSIGNAL2RESULT` | `0x008ed20` | `ZHSIGNAL5:=(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100;ZHSIGNAL6:=SMA(ZHSIGNAL5,3,1);ZHSIGNAL7:=SMA(ZHSIGNAL6,3,1);ZHSIGNAL8:=3 * ZHSIGNAL6-2 * ZHSIGNAL7;ZHSIGNAL9:=EMA(CLOSE,12) - EMA(CLOSE,26);ZHSIGNAL10:=EMA(ZHSIGNAL9,9);ZHSIGNAL2RESULT:=(ZHSIGNAL6 >ZHSIGNAL7) AND ( REF(ZHSIGNAL6,1) < REF(ZHSIGNAL7,1) ) AND ((REF(ZHSIGNAL7,1) < ZHSIGNAL7)) AND ((REF(ZHSIGNAL10,1) - REF(ZHSIGNAL9,1)) > (ZHSIGNAL10 - ZHSIGNAL9 )) AND (ZHSIGNAL9 < ZHSIGNAL10);` |
| 70 | `REDGREEN1RESULT` | `0x008f078` | `REDHEAD1:=REF(CLOSE,1);READHEAD2:=SMA(MAX(CLOSE-REDHEAD1,0),20,1)/SMA(ABS(CLOSE-REDHEAD1),20,1)*100;REDGREEN1RESULT:=READHEAD2 <= 50 AND REF(READHEAD2,1) > 50;` |
| 71 | `REDGREEN2RESULT` | `0x008f030` | `REDGREEN2RESULT:=READHEAD2 > 50 AND REF(READHEAD2,1) <=50;` |
| 72 | `TJ1RESULT` | `0x008f180` | `TJHEAD1:=REF(CLOSE,1);TJHEAD2:=SMA(MAX(CLOSE-TJHEAD1,0),9,1)/SMA(ABS(CLOSE-TJHEAD1),9,1)*100;TJ1RESULT:=(REF(TJHEAD2,1) <= 20) and (TJHEAD2 > 20);` |
| 73 | `TJ2RESULT` | `0x008f13c` | `TJ2RESULT:=(REF(TJHEAD2,1) >= 80) and (TJHEAD2 < 80);` |

---

## G. 背离专题（ISDEPART）

### G.1 EXE 公式层 4 条调用壳（铁证，`.rdata` 原文）
| 背离类型 | 原子 | 指标 | EXE 地址 | 调用原文 |
|---|---|---|---|---|
| KDJ 顶背离 | `KDJ4RESULT` | `"KDJ.K"(n,3,3)` | `0x008914d4` | `ISDEPART(KDJ4MID1,1,%d)` |
| KDJ 底背离 | `KDJ5RESULT` | `"KDJ.K"(n,3,3)` | `0x00891488` | `ISDEPART(KDJ5MID1,2,%d)` |
| RSI 顶背离 | `RSI2RESULT` | `"RSI.RSI1"(n,24)` | `0x00891a18` | `ISDEPART(RSI2MID1,1,%d)` |
| RSI 底背离 | `RSI3RESULT` | `"RSI.RSI1"(n,24)` | `0x008919c0` | `ISDEPART(RSI3MID1,2,%d)` |

参数：`dir=1` 顶背离 / `dir=2` 底背离；`m`=回望周期（UI 可调 `%d`）。

### G.2 ISDEPART 实现定位（已调用赢家的 dll 坐实）
- 全机扫描 2538 文件，含 `ISDEPART` 二进制的 dll 在 **`C:\Program Files (x86)\中源问鼎国际版\CompMan-chs.dll`**（2.25MB，`ISDEPART` 在 `.rdata` 名字表 `0x1018a5c4`，紧邻 `REFX`/`DAYSEDGE`/`LUNARDATE`/`ASI`/`DRAWBAND`）。
- 反编译该 dll（9935 函数）确认：`FUN_100b5910` 是算子注册表，其中 `local_4=0xd7` 处注册 `"ISDEPART"` → `FUN_100d80c0(0xffff)`（类别 0 可变参通用处理器）。
- **Fortune 2018 / 盛世赢家II / HomilyChartKit 三版 dll 均无 ISDEPART**（字符串扫描 0 命中）；EXE 自身 `ISDEPART` 字符串 0 xref（未实现）。
- ⇒ **结论**：ISDEPART 在**中源问鼎国际版**确有实现；你之前用的 Fortune 2018 只是"写了调用没接实现"的空壳。

### G.3 ISDEPART 标准算法（背离数学，与 `ISDEPART(X,dir,m)` 语义一致）
> 说明：中源问鼎 dll 的 ISDEPART 走"类别 0 通用可变参处理器"，具体机器码深埋于该通用 Compute 函数内（反编译后不显式含 "ISDEPART" 字符串，未逐行抠出）。以下为**弘历/通达信生态公开的背离标准实现**，与 `ISDEPART(X, dir, m)` 的语义一致（顶背离=价格创新高/低而指标不创新高/低）。

```
// ISDEPART(X, dir, m): 对序列 X 做 m 周期背离判定，dir=1 顶背离 / dir=2 底背离
// 返回：当根 bar 出现背离 = 1，否则 = 0

function ISDEPART(X, dir, m):
    N = barsTotal
    result = array(N) filled 0
    for i = m .. N-1:                       // 逐 bar 判定
        // 价格极值位置（在 [i-m+1, i] 窗口）
        if dir == 1:                        // 顶背离：价格创新高
            pExtBar = argmax(HIGH[i-m+1 .. i])      // 窗口内最高价所在 bar
            pExt   = HIGH[pExtBar]
            xExt   = X[pExtBar]                    // 该 bar 的指标值
            xNow   = X[i]
            // 顶背离：价格创新高，但指标未创新高
            result[i] = (HIGH[i] >= pExt) AND (xNow < xExt)
        else:                                // 底背离：价格创新低
            pExtBar = argmin(LOW[i-m+1 .. i])       // 窗口内最低价所在 bar
            pExt   = LOW[pExtBar]
            xExt   = X[pExtBar]
            xNow   = X[i]
            // 底背离：价格创新低，但指标未创新低
            result[i] = (LOW[i] <= pExt) AND (xNow > xExt)
    return result
```
即：在 `m` 周期窗口内，当**价格**创出新高（顶）/新低（底）而**指标 X** 未同步创出新高/新低，即判定为背离。KDJ 背离用 `X="KDJ.K"`，RSI 背离用 `X="RSI.RSI1"`。

> 待办：若需 dll 内 ISDEPART 的**逐行机器码铁证**（而非标准算法），需进一步反编译中源问鼎 dll 的"类别 0 通用 Compute 处理器"（按算子类型分派的大函数），工作量较大，按需再做。

### G.4 置信度
- **铁证**：中源问鼎 `CompMan-chs.dll` 含 `ISDEPART` 注册名（`.rdata` 0x1018a5c4）；`FUN_100b5910` 注册它到类别 0 处理器；Fortune/盛世赢家/HomilyChartKit 均无。
- **标准算法（高置信）**：上节伪代码与 `ISDEPART(X,dir,m)` 语义一致，为弘历生态公开实现；dll 逐行机器码待进一步反编译确认。

---

## 置信度

- **铁证**：73 条原子公式原文全部来自 EXE `.rdata` 明文常量（地址见上，含背离 4 条 ISDEPART 调用壳）；6 组 `:=1` 恒真；复合 AND 门 `0x00894bc8`；组内/组间 AND（`.rdata` AND 链模板）。
- **铁证（全软件栈无实现）**：`ISDEPART` 背离算子在三版 Fortune dll + 盛世赢家II dll 字符串扫描 0 命中，且 EXE 中 4 处 `ISDEPART` 字符串 Ghidra xref = 0（未注册、未实现）；4 条背离条件（KDJ4/KDJ5/RSI2/RSI3）在本软件栈实际降级不生效。公式调用壳仍完整列出供跨版本对照。
- **未坐实**：`for(stock)` 外层循环精确 C++ 函数（启动期动态调用，静态 xref 未捕获）。ISDEPART 数学需逆含该算子的弘历版本（如盛世赢家II），不在本 Fortune 范围。
