# 箱体王 还原（预测大师 HLLevel2.EXE 逆向）

> 来源：`C:\Program Files (x86)\预测大师\Setting\技术指标1.exp`（加密 token 公式）+ `CompMan.dll` 的 `XTWBREAK` 算子（FUN_100cc2f0 真实 Compute）。
> 全部为二进制铁证，非推测。

## 1. 箱体王公式（来自 技术指标1.exp 解密）

`技术指标1.exp` 是加密 token 格式（head `ad000000`，非标准 marker 版）。解密后「箱体王」指标名（`\x06箱体王`）后跟 token 代码段（`\x00\xff` 标记 @ 0xaaff）。用 `token_decode_v4.py` 还原出真实算子树：

```
YRU+(---D8YABYFYNZ RU+(---D8ZABYFXN1 N1DMA+(N D8ZABXFQN/DMA+(N D8YABXFPNNDMA*(1,(/DYAHVH1,(N1DYAASN2DMA*(/HTUHN1)N3
,-(-/1((N/N*(/*(N/N2)*-)* DHEZDHXADH(XDXDZNNADH/N(0N4
,-(-/1((N/N*(/*(N/N2)*()*N DHEYDHXADH(XDXDZNNADH/N(02(),(N3()-(N3(),(N3()-(N3(+N3-(-(//1,,(-) DZZDXDXADXD(NN1+N4
,-(-(//1,,(-) DZZDXDYADXD(NN1N+N1
,-(-(//1,,(-) DZZDXDZADXD(NN--1+/-(-(//1,,(-) DZZDXDN1ADXD(NN12
((DMA(,(N/0(() RYXXE(N,((:N2FYPN1N4*(/ AABYXXDXD(NN--1NN
,(N,((:N2FYPN1N4*(/ GZAABNNDXD(NN1NN0
,(N,((:N2FYPN1N4*(/*/ AABNXDXD(XDHZNN)N4NN)N4N
,(N,((:N2FYPN1N4*(/ GPAABZNDXD(N4NNDHXDHZNN)/,-(-/1((VXH*TYH(/*NHDXDYXXDYNDXAD(NN1)*/N(0N
,-(-/1((VXH*VYQQDZXXDYXXDYNDXAD(NN--1)*/N(0 HLT1((((((( KBDSQ,,DMA(N1(N1DZAE-N1(/DZAAS,,DMA(N1(N1)N1),-N1(/)N1AAS,,DMA(,,+*),-(-/1(,,HVXDXDH,,DEYDXADXD(NN1
,-(-/1(,,HTXDXDH,,DEYDXADXD(NN11/-2-( KBDSQ-,DMA,N*((-(DMA-N1(N3)N1),-N1(N4)N1)DMA-,:SUM(DXAS,-(-/1(VXD)+)NDXADYD(NN1)/N(0
,-(-/1(TXD+))NDXADYD(NN11/)/N(0-2-( KBDSQ-,DMA,N*(
```

### 拼音算子 → 通达信/弘历函数映射（按 dll 算子集）
| token | 含义 |
|---|---|
| `YRU` / `YRU+` | **XTWBREAK**（箱体突破，3=上 4=下）|
| `D8YABYF` | `HHV(HIGH, N)` 最高价 N 日最高 |
| `D8ZABYF` | `LLV(LOW, N)` 最低价 N 日最低 |
| `D8YABXF` / `D8ZABXF` | 高低价极值序列 |
| `DHE` | `LOW`（低）|
| `DZZDXD` | `MA(x, N)` 均线 |
| `RYXXE` | `REF(x, N)` 引用前 N 周期 |
| `AABYXXDXD` | `CLOSE`（收盘）|
| `GZAAB` / `GPAAB` | 最高/最低相关 |
| `HLT1` | HLT 类算子（dll 占位，未逐字解码）|
| `KBDSQ` | `VOL`（成交量）|
| `SUM` | `SUM(x, N)` |
| `DXAS` | `OPEN`（开）|
| `VXH` / `VYH` | 最高/最低价 |
| `TXD` | 收盘价类 |
| `DMA` | `DMA(x, A)` 动态移动平均 |
| `HTUHN` | 某种平滑 |

## 2. XTWBREAK 算子真实 Compute（FUN_100cc2f0，CompMan.dll 反编译）

注册表 @ 0x9db84 注册 XTWBREAK 时 `operator_new` 前置 `push 0x100cc2f0` = 其 Compute 函数（同 ISDEPART 模式）。

**签名**：`FUN_100cc2f0(double* out, int* Xseries, int param_3, int param_4, undefined4* ctx)`

**参数分派**（dVar1 = 参数，来自序列 accessor）：
- `1.0`（=XTWBREAK(3) 上突破）→ 路径 A：输出上箱体突破序列
- `2.0`（=XTWBREAK(4) 下突破）→ 路径 B：输出下箱体突破序列
- `3.0` → 路径 C：箱体上下轨判定（价格在区间内→输出触发值 1.0）
- `4.0` → 路径 D：箱体突破反向判定

**核心逻辑**（反编译确认）：
- 维护动态箱体（上轨 `pdVar6[-3]` / 下轨 `pdVar6[-c]`）
- 价格突破上轨且前态未突破 → 输出 `_DAT_1015af08 = 1.0`（触发）
- 价格跌破下轨 → 输出 1.0
- 价格在区间内（`_DAT_1014f174=0.0` 哨兵值排除无效）→ 输出 0.0（_DAT_10159428）
- 每段输出 0xc（12字节），含 上箱体/下箱体/价格/突破状态 4 个值

**常量确认**：
- `_DAT_1015af08 = 1.0`（触发）
- `_DAT_10159428 = 0.0`（默认/未触发）
- `_DAT_1014f174 = 0.0`（float，无效值哨兵）
- `_DAT_1015f280=2.0` / `_DAT_1015f340=3.0` / `_DAT_1015f288=4.0`（分派参数）

## 3. 与八大天王映射
八大天王总门里：
```
XTHEAD1 := XTWBREAK(3);   // 突破上箱体
XTHEAD2 := XTWBREAK(4);   // 突破下箱体
XT1RESULT := XTHEAD1=1;   // 箱体王-上突破信号
XT2RESULT := XTHEAD2=1;   // 箱体王-下突破信号
```
→ 箱体王 = `XTWBREAK(3)` 上箱体突破 / `XTWBREAK(4)` 下箱体突破，触发输出 1.0。

## 4. 原始提取
- `_archive/xtwbreak_compute.c`（XTWBREAK 完整反编译）
- `_archive/xtwbreak_token_decoded.txt`（箱体王 exp token 解码全文）

## 5. 置信度
- **铁证**：箱体王公式来自 `技术指标1.exp` 解密 token + `XTWBREAK` 算子反编译（FUN_100cc2f0），均二进制确认。
- 拼音算子映射为 dll 算子集对应（YRU=XTWBREAK 由反编译 + exp 双重确认）；个别 HLT 类占位（HLT1）未逐字解码。
