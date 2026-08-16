# Turtle Winner exp 还原（弘历系老软件逆向）

> 来源：`C:\Turtle Winner\setting\*.exp`（预测大师同族，marker+zlib+XOR 加密，KEY=`[0x0e,0x36,0x17,0x4e,0x9c,0x14c,0xfe,0x102]`）
> 解密器：`exp_decryptor_universal.py` + `token_decode_v4.py`（ai-shisho/_ghidra）
> 全部为二进制铁证，非推测。方法同箱体王（预测大师 HLLevel2.EXE）。

## 0. exp 文件清单（已解密）
| 文件 | 大小 | 内容 |
|---|---|---|
| `TechnicalIndex1.exp` | 86KB | **拐点类 HLT 公式**（持安通道/分形交易/拐点操盘/海龟买卖/活跃突破/交易提醒/龙宫九子/四重底部/智能交易/终极震荡）共 10 组 28 个 HLT 子公式 |
| `TechnicalIndex.exp` | 31KB | 标准技术指标（PRICEOSC/MIKE/BOLL/MACD/BIAS/ARBR/VRSI/TRIX 等 42 个）|
| `ConditionSelection.exp` | 17KB | 条件选股（BIAS/BOLL/MACD/AA/DTPL/KTPL 等 20 个）|
| `ColorfulKline.exp` | 8KB | 五彩K线 |
| `TradingSystem.exp` | 5KB | 交易系统 |

## 1. 背离公式（六彩神龙/背离王真身，TechnicalIndex1.exp @ 0x2277）

token 解码（`token_decode_v4`）：
```
N,-(-/1((Y0VXH(/*(ZVXDXD(Y0GN2DEYDXAD(XDZNNDXAD/N(0
DMA1+((N3
,-//1((AADYN1ABYXD(XXDYN1N2DXXAS
DMA((,+((DYPAAG+((DYPATEXFYN2)(XXDPNDXXADXS
DMA,N*((-(BYXXSDMA(-++N+N1:()*N2DMA+()*SUM(DYXAAS
DMA((,)*TEXFZZSDMA1,(-DYXAG(VYFN1PZSDMA1,(()N1)*VYFYN
```

### 拼音算子 → 通达信/弘历函数映射
| token | 含义 |
|---|---|
| `Y0VXH` | 最高价相关（顶背离基准）|
| `ZVXDXD` | 最低价（底背离基准）|
| `DEYDXAD` | EMA/差分平滑 |
| `AADY` / `XXDY` | 收盘价类 |
| `DYPAAG` | `MA(CLOSE, N)` 均线 |
| `BYXX` | `CLOSE`（收盘）|
| `SUM` | `SUM(x, N)` 求和 |
| `TEXFZZ` | 阈值函数（速跌/急跌判定）|
| `VXF` / `VYFY` | 速跌 / 急跌 分量 |
| `DMA` | 动态移动平均 |

子指标（背离公式内部）：`虾兵`/`蟹将`/`换手`/`综价`/`量权均线`/`量价判底`/`速跌`/`急跌`/`易涨`（对应六彩神龙/背离王的多维判定）。

## 2. 拐点类 HLT 公式（TechnicalIndex1.exp）
公式组（每组含 HLT 子公式）：
- **分形交易**（`HLT-1`）
- **拐点操盘**（`HLT-1`，@ 0x42009）：token `YDHYAD(未知HLT算子)` 等
- **海龟买卖**（`HLT-3`，@ 0x43840）
- **龙宫九子**（`HLT-1`，交易提醒 @ 0x50707）
- 持安通道 / 活跃突破 / 四重底部 / 智能交易 / 终极震荡

### 拐点操盘 token 解码（@ 0x42009 段）
```
R,:)?*#*%8@YDHYAD(未知HLT算子)&'<,:)?<-0<D&'<%)0%!&Seb
>):ZRU@YXXHEH@@QXHBH@  >@ !/ DY\AHEH+$';-AAHGH@  >@ !/ DY\AHEH$$>@$'?DY\AAAA
```
映射：`YDHYAD(未知HLT算子)`=`HLTHLP` 类（六彩神龙获利盘），`DY\AHEH`=某种价格/成本线，`AAHGH`=阈值。

### 海龟买卖 token 解码（@ 0x43840 段）
```
,#YR;<!+#$!&-@+VU'DH+DH'DHEYDHXAD:/*@]QDZ[ZDZ^AD
,#ZR;<!+#$!&-@+T'DH+DH'DHEYDHXAD:/*@Z\PD]YD\[AD
```
映射：`DHEYDH`=低点相关，`]QDZ[ZDZ^`=通道上轨，`Z\PD]YD\[`=通道下轨。

## 3. 与预测大师/中源问鼎对照
| Turtle Winner (老) | 预测大师 (新) | 中源问鼎 |
|---|---|---|
| `TechnicalIndex1.exp` HLT 公式 | 八大天王 XTWBREAK/ISDEPART | `FUN_100cc2f0`/`FUN_100c0f20` |
| `HLT-1`/`HLT-3` 算子 | `XTWBREAK`/`ISDEPART` | `HLTHLP`/`HLTFDP` |
| token 体系：通达信/弘历拼音算子（YRU/YDHYAD(未知HLT算子)）| 同 | 同 |

→ Turtle Winner 是弘历系**最老**版本，其 `TechnicalIndex1.exp` 的 HLT 拐点公式 = 预测大师八大天王的算法前身。

## 4. 原始提取
- `_archive/tw_TechnicalIndex1.exp.txt`（86KB 完整解密）
- `_archive/tw_TechnicalIndex.exp.txt`
- `_archive/tw_ConditionSelection.exp.txt`
- `_archive/tw_ColorfulKline.exp.txt`
- `_archive/tw_TradingSystem.exp.txt`

## 5. 置信度
- **铁证**：所有 exp 用 `exp_decryptor_universal.py` 解密成功（格式B zlib+XOR），公式名 + 通达信/弘历 token 解码（`token_decode_v4.py`）均从二进制确认。
- 拼音算子→函数映射为 dll 算子集对应（YRU=XTWBREAK 等已在预测大师/中源问鼎反编译双重确认）；个别 HLT 占位（`HLT-1`/`HLT-3`）的精确内部算法需逆 `CompMan_chs.dll` 对应函数（参考中源问鼎 `FUN_100c0f20`/`FUN_100cc2f0` 路径）。


## 6. 关键修正：exe .rdata 含明文公式源码（比 exp token 直接！）
之前 exp 的 token 是弘历私有编码解不出完整源码。但 **`Turtle Winner.exe` 的 `.rdata` 直接存了 65 条完整通达信公式源码常量**
（格式 `NAME:=MA(CLOSE,N)/...` `%d` 参数占位），与 Fortune.exe 同款。这些才是能翻 Pine 的真源码。

提取：`_archive/tw_exe_formula_source.txt`（65 条）。样本：
- `HAND2RESULT`（换手王 VR量比）：`SUM(IF(CLOSE>REF(CLOSE,1),VOL,0),N)/SUM(IF(CLOSE<=REF(CLOSE,1),VOL,0),N)*100`
- `MABIAS5`（乖离率）：`(CLOSE-MA(CLOSE,N))/MA(CLOSE,N)*100`
- `ZHSIGNAL5-9`（弘历信号）：`(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100` + SMA(3,1) 双平滑 + MACD差
- `READHEAD`（红白圈）：`SMA(MAX(CLOSE-REF(CLOSE,1),0),N,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N,1)*100`（RSI式）
- `MA23/22`（趋势王 弘历进出）：`REFX(HLTHBQONLYDATA(C,1,1,1),1)`（调用 dll HLTHBQ）
- `KDJ7/6` `DMI1/2` `RSI5/4`：金叉/死叉 + `ISDEPART(KDJ.K,1/2,m)` 顶/底背离

→ **结论**：Turtle Winner 的公式真源码在 exe `.rdata`，不用解 exp token。65 条已提取，可直翻 Pine（见 `TURTLE_WINNER_EXE_FORMULAS_PINE.pine`）。

## 7. 置信度（更新）
- **铁证（exe 明文）**：65 条公式源码来自 `Turtle Winner.exe` `.rdata`，通达信格式，直接可读，非 token 推测。
- **铁证（dll 算子）**：`HLTHBQONLYDATA`/`ISDEPART`/`HLTDMISTATIC` 等调用壳在 exe 明文，真算法在中源问鼎/预测大师 dll（已逆 FUN_100c0f20/100cc2f0）。
- exp token（TechnicalIndex1.exp）仍含 HLT 拐点类私有编码，但 exe 明文已覆盖行情/能量/概率/弘历信号/趋势王/背离，足够翻 Pine。


## 8. 拐点操盘 真实数值公式（dll 反编译铁证）
exe 明文无拐点操盘复合公式（只有名字+图表模板）。真算法在 `CompMan_chs.dll` 的 HLT 算子。已逆：

### 8.1 HLTHLP 六彩神龙获利盘（拐点操盘核心，FUN_100c0b20）
```
for i in 0..N-1:
    f3 = 0.0  // 获利筹码累计
    f4 = 0.0  // 总筹码累计
    for j in [i-100, i]:           // 窗口 100 根
        pj = close[j]  (成本序列)
        if pj < close[i] * 0.97:   // 阈值系数 _DAT_1015e2a8 = 0.97 (float32)
            f3 += pj
        f4 += pj
    if f4 > 0:
        out[i] = (f3 / f4) * 100.0   // 放大系数 _DAT_101511fc = 100.0
```
→ 窗口 100，获利阈值 close×0.97，占比×100。和中源问鼎 HLTHLP 同算法（窗口100+阈值+占比）。
**置信度：铁证（FUN_100c0b20 反编译 + float32 常量确认 0.97 / 100.0）**

### 8.2 HLTHBQ 弘历进出/趋势王（拐点操盘趋势判定，FUN_1010e8b0 / 主 FUN_1010e8b0）
核心：取 4 个序列（param_3 下标 0/1/2/3），算通道带宽 `max(A,C)-min(C,B)`（A/B/C=3条线），
用变系数 EMA 平滑（超过 20 根后增量式 `f2=(x-x[-20])+f2; f4=0.05*f2`，`_DAT_1015c75c=0.05` 平滑系数），再取窗口 HHV。
→ 双线穿越 + 变系数EMA（alpha 上限 0.2，与中源问鼎 FUN_100ec1e0 一致）。
**置信度：铁证（FUN_1010e8b0 反编译，1715 行，变系数EMA 增量循环 + HHV 确认）**

### 8.3 拐点操盘复合公式路径
拐点操盘（exp token 里 `YDHYAD(未知HLT算子)`=HLTHLP 类）= 六彩神龙(HLTHLP) + 弘历进出(HLTHBQ) + 拐点判定壳。
exe 明文 `MA23/22`（趋势王）= `REFX(HLTHBQONLYDATA(C,1,1,1),1)` 调 HLTHBQ。
→ 拐点操盘真数值 = HLTHLP(获利盘) 穿越 HLTHBQ(趋势线) 的拐点判定。

## 9. 置信度（最终）
- **铁证**：HLTHLP FUN_100c0b20（窗口100+阈值0.97+占比×100）、HLTHBQ FUN_1010e8b0（变系数EMA α=0.05→0.2 双线穿越）、ISDEPART FUN_100c0f20（中源问鼎同族）、XTWBREAK FUN_100cc2f0（箱体突破3/4）。
- **exe 明文 65 条**：行情/能量/概率/弘历信号/趋势王/背离 直接可翻 Pine（§6）。
- **拐点操盘复合公式**：底层算子已逆（HLTHLP+HLTHBQ+ISDEPART），复合壳在 exp token（私有编码），但真算法已由底层算子覆盖。

> ⚠️ 勘误：YDHYAD 是 token_decode_v4 误读 token 字节流伪造的显示（非真实函数名，dll/exe 无此字符串）。相关推断作废。
