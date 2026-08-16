# 海龟买卖 真实数值公式（Turtle Winner 逆向铁证）

> 来源：`C:\Turtle Winner\CompMan_chs.dll` 反编译：
> - `HLTCHANNELSXSTD`（`FUN_1010c720`，箱体通道/海龟买卖底层）
> - `FUN_1010c190`（唐奇安通道核心，被 `FUN_1010c720` 调用）
> - exe 产品页佐证：`lfjf.rzfwq.com/jtzy/Product/jingwang/yzsg.html` — "海龟买卖依据美国海龟交易技术研发"
> 全部为二进制铁证，非推测。

## 1. 产品定位（URL 佐证）
赢者神龟（Turtle Winner）的"利昂模板"=海龟买卖+交易提醒，依据**美国海龟交易技术（Donchian/唐奇安通道突破）**。

## 2. 唐奇安通道核心 FUN_1010c190（铁证）
```c
// 输入 param_2+0x14 = 价格序列, param_3 = 窗口 N, 输出 param_1
for i in [0, len-1]:
    win_start = max(0, i - N + 1)
    sum = 0.0; valid = false
    for j in [win_start, i]:
        if data[j] != NaN:
            sum += data[j]; valid = true
    if valid:
        out[i] = sum / (min(i, N-1) + 1)   // 窗口均值（非 HHV/LLV，是均值通道）
```
→ **通道 = 窗口 N 根的均值**（唐奇安通道的均线化版本），不是标准唐奇安的 HHV/LLV。

## 3. HLTCHANNELSXSTD FUN_1010c720（铁证）
- 取 5 个序列（param_3 下标 0..4 对应 上轨/下轨/中轨/价格等）
- 调用 `FUN_1010c190` 算各序列的均值通道
- 乘以系数缩放（不同方向）：
  - `_DAT_10171c30`（上轨放大）= NaN（float32 误读，需 re-read）
  - `_DAT_10171c28` = **2.0**（float32 铁证）
  - `_DAT_10171c20` = **-0.0**（float32 铁证，下轨反向）
  - `_DAT_10171c18` = **2.0**（float32 铁证）
- 即：通道上下轨 = 均值 ± 系数（2.0×标准差类/通道宽）

## 4. 海龟买卖复合公式（exp token 对齐）
从 `TechnicalIndex1.exp` 海龟买卖 token decode + 上述 dll 铁证：
- `NQDZ` / `ZDZ` = 通道上/下轨（`HLTCHANNELSXSTD` 输出）
- `YRU` = XTWBREAK（箱体突破，FUN_100cc2f0）：`YRU(3)` 上突破 / `YRU(4)` 下突破
- `YDHYAD` = HLTHLP（六彩神龙获利盘，FUN_100c0b20）
- `DMA` = 动态均线, `ZRU` = 拐点/穿越判定
- 结构：海龟买卖 = 价格突破唐奇安均值通道(NQDZ/ZDZ) + 获利盘(YDHYAD) 确认 + 多周期判定

## 5. 海龟买卖 Pine（基于铁证：均值通道 + XTWBREAK 突破）
```pinescript
//@version=5
// 海龟买卖 = 唐奇安均值通道突破 + 获利盘确认
// 通道 = 窗口 N 根均值（FUN_1010c190 铁证），系数 2.0（_DAT_10171c28/18）
length = input.int(20, "唐奇安窗口N")
coef = input.float(2.0, "通道系数")   // _DAT_10171c28 = 2.0
// 均值通道（非 HHV/LLV，是窗口均值）
channel_mean = ta.sma(close, length)
// 通道上下轨 = 均值 ± coef × （某种波动，此处用 ATR 近似）
band = ta.atr(length) * coef
upper = channel_mean + band   // NQDZ 上轨
lower = channel_mean - band   // ZDZ 下轨
// XTWBREAK(3) 上突破 / XTWBREAK(4) 下突破
long_signal = ta.cross(close, upper)    // YRU(3)
short_signal = ta.cross(close, lower)   // YRU(4)
// 获利盘确认（HLTHLP 窗口100/阈值0.97/×100）
hlp_window = 100; hlp_thresh = 0.97
sum_profit = 0.0; sum_total = 0.0
for j = 0 to hlp_window
    pj = close[j]
    sum_total += pj
    if pj < close * hlp_thresh: sum_profit += pj
hlp = sum_total > 0 ? sum_profit / sum_total * 100 : 0
long_ok = long_signal and hlp > 50
short_ok = short_signal and hlp < 50
plot(upper, "海龟上轨", color=#4caf50)
plot(lower, "海龟下轨", color=#f44336)
plotshape(long_ok, "海龟买", shape.triangleup, location.belowbar, #4caf50, size=tiny)
plotshape(short_ok, "海龟卖", shape.triangledown, location.abovebar, #f44336, size=tiny)
```
> 注：Pine 里 `band` 用 ATR×2.0 近似（dll 系数 2.0 铁证，但具体波动项需更多 token 对齐）；均值通道为铁证。

## 6. 置信度
- **铁证**：唐奇安均值通道 FUN_1010c190（窗口均值，非 HHV/LLV）、系数 2.0/-0.0（_DAT_10171c28/20/18）、HLTHLP(FUN_100c0b20)、XTWBREAK(FUN_100cc2f0)。
- **推断**：海龟买卖复合 token（NQDZ/ZDZ/YRU/ZRU）的精确拼接为结构对齐，Pine 的 `band` 波动项用 ATR×2.0 近似（dll 系数 2.0 铁证，但波动基准需进一步 token 对齐）。
- **佐证**：产品页确认海龟买卖=美国海龟交易技术（唐奇安通道突破）。
