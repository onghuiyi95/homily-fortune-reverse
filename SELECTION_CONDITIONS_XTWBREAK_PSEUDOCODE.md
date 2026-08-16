# 箱体王 伪代码白皮书（逐行对照版）

> 基于：`技术指标1.exp` 解密 token（YRU=XTWBREAK）+ `CompMan.dll` FUN_100cc2f0 反编译。
> 格式：逐行 `变量=表达式  // 注释`，方便对照 TradingView / 通达信 报错逐行核对。

## 一、箱体王主指标（exp 解码还原）
// 箱体王 = 动态上下轨箱体 + 突破判定
// N = 窗口参数（exp token 里 N1/N2/N3/N4 为不同周期的轨）

UPPER_BOX = HHV(HIGH, N1)        // 上箱体轨：N1 日最高价  (token: D8YABYF, N1)
LOWER_BOX = LLV(LOW, N1)         // 下箱体轨：N1 日最低价  (token: D8ZABYF, N1)

UPPER_BOX2 = HHV(HIGH, N2)       // 次级上轨 (token: D8YABXF, N2)
LOWER_BOX2 = LLV(LOW, N2)        // 次级下轨 (token: D8ZABXF, N2)

MID_BOX = (UPPER_BOX + LOWER_BOX) / 2      // 箱体中轴 (token: D8YABXFPNNDMA*(1,...)

// 动态均线平滑轨（DMA 类）
BOX_MA = DMA(CLOSE, A)         // 收盘价动态移动平均 (token: DZZDXD + AABYXXDXD, DMA)

// 突破判定（XTWBREAK 算子，FUN_100cc2f0）
BREAK_UP   = XTWBREAK(3)       // 上箱体突破：价格突破上轨→1，否则→0  (token: YRU, 参数3)
BREAK_DOWN = XTWBREAK(4)       // 下箱体突破：价格跌破下轨→1，否则→0  (token: YRU, 参数4)

// 成交量确认（token: KBDSQ=VOL, SUM, DMA）
VOL_MA = DMA(VOL, A)                  // 量动态均 (token: KBDSQ,,DMA)
VOL_SUM = SUM(VOL, N3)                // 量求和 (token: SUM(DXAS...))  注 DXAS=OPEN 实际为量区间
VOL_COND = VOL > VOL_MA * R           // 突破伴随放量确认 (token: VXD)+)NDXADYD

// 箱体王输出（多段数组，每段 0xc=12 字节：上轨/下轨/价格/突破态）
BOX_STATE[i] = (                        // XTWBREAK 内部逻辑（FUN_100cc2f0 反编译）：
    CLOSE[i] > UPPER_BOX[i]  ? 1.0      // 路径A：上突破触发 _DAT_1015af08=1.0
  : CLOSE[i] < LOWER_BOX[i]  ? 1.0      // 路径B：下突破触发
  : 0.0)                                // 区间内未触发 _DAT_10159428=0.0
  // 无效值哨兵 _DAT_1014f174=0.0 排除（上市首日/数据缺失）

## 二、XTWBREAK 算子逐行伪代码（FUN_100cc2f0 逆）
// 调用：XTWBREAK(mode)  mode=3 上突破 / mode=4 下突破
// 输入：CLOSE/HIGH/LOW 序列 + 动态箱体上下轨
// 输出：out[] 序列（每段12字节，含 上轨/下轨/价格/突破态 4 值）

spj = CLOSE[i]              // 当前收盘价  (token: AABYXXDXD)
sh  = HIGH[i]               // 当前最高价  (token: VXH)
sl  = LOW[i]                // 当前最低价  (token: VYH)
up  = UPPER_BOX[i]          // 当前上箱体轨 (pdVar6[-3])
dn  = LOWER_BOX[i]          // 当前下箱体轨 (pdVar6[-c])

if mode == 3:               // 上突破 (路径A, dVar1=1.0)
    if spj > up:            // 价格突破上轨
        XT1RESULT = 1       // 输出触发 _DAT_1015af08
    else:
        XT1RESULT = 0       // _DAT_10159428

if mode == 4:               // 下突破 (路径B, dVar1=2.0)
    if spj < dn:            // 价格跌破下轨
        XT2RESULT = 1
    else:
        XT2RESULT = 0

// 箱体内部判定（路径C/D，dVar1=3.0/4.0）
if up != 0.0 and dn != 0.0 and (dn < spj and spj < up):   // 价格在区间内
    BOX_INSIDE = 1.0        // _DAT_1015af08 区间内标记
else:
    BOX_INSIDE = 0.0

## 三、八大天王里的箱体王（总门引用，铁证）
XTHEAD1 := XTWBREAK(3);     // 上箱体突破序列
XTHEAD2 := XTWBREAK(4);     // 下箱体突破序列
XT1RESULT := XTHEAD1 = 1;   // 箱体王信号：突破上箱体
XT2RESULT := XTHEAD2 = 1;   // 箱体王信号：突破下箱体

## 四、置信度
- 箱体王 = XTWBREAK(3 上 / 4 下) + 动态 HHV/LLV 箱体轨：exp token(YRU/D8YABYF/D8ZABYF) + 反编译(FUN_100cc2f0) 双重铁证。
- 具体 N1/N2/N3/N4 周期值与 A（DMA 平滑系数）为 exp 默认参数，UI 可调；token 流里 N1/N2/... 为占位，真实数值在公式注册参数表。
- 个别 HLT 类算子（HLT1 占位）未逐字解码，不影响箱体王主逻辑（主逻辑 = XTWBREAK + HHV/LLV 箱体）。
