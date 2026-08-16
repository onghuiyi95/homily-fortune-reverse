# 八大天王 真实公式（预测大师 / HLLevel2.EXE 逆向）

> 来源：`C:\Program Files (x86)\预测大师\HLLevel2.EXE`（用户校准：八大天王在这里，不在 Homily Fortune）
> 全部为 EXE `.rdata` 明文常量铁证（公式块 @ 0x008da208 起），非推测。
> 注意：`Homily Fortune` 里**没有**八大天王——之前把 Fortune 的通用原子误标为"八大天王"已删除（见 SELECTION_CONDITIONS_TOP.md）。

## 0. 八大天王 UI（铁证）
标签 `八大天王`（@ 0x008c43ac）；8 个分组标签：
`操盘王` `箱体王` `多空王` `波段王` `趋势王` `MACD` `背离王` `换手王` `强弱王`（共 8 王，强弱王为第 8 个）

## 1. 八大天王总门（铁证 @ 0x008da208）
```
HLWANGRESULT:=1
  AND HS2RESULT AND HS1RESULT       // 换手王
  AND QR4RESULT AND QR3RESULT AND QR2RESULT AND QR1RESULT   // 强弱王
  AND BL4RESULT AND BL3RESULT AND BL2RESULT AND BL1RESULT  // 背离王
  AND XT2RESULT AND XT1RESULT        // 箱体王
  AND DK2RESULT AND DK1RESULT        // 多空王
  AND CP2RESULT AND CP1RESULT        // 操盘王
  AND BD2RESULT AND BD1RESULT        // 波段王
  AND WANG4RESULT AND WANG3RESULT AND WANG2RESULT AND WANG1RESULT  // 趋势王
```
全部 AND（非 OR）。

---

## 2. 各王原子公式（.rdata 原文）

### 2.1 换手王 HS（强于/弱于大盘 + 飘带）
```
HSHEAD1 := 100*VOL/CAPITAL;                  // 换手率%
HSHEAD2 := SUM(HSHEAD1,40);                  // 40日换手和
HSHEAD3 := MA(HSHEAD2,20);                   // 20日均
HS1RESULT := CROSS(HSHEAD2,HSHEAD3);         // 飘带绿变红（强于均）
HS2RESULT := CROSS(HSHEAD3,HSHEAD2);         // 飘带红变绿（弱于均）
```

### 2.2 强弱王 QR
```
QRHEAD1 := HLTEXPERTQRW(C,14,1);             // 个股强弱线（弘历专家强弱）
QRHEAD2 := HLTEXPERTQRW("1A0001$C",14,1);    // 大盘(上证)强弱线
QR1RESULT := QRHEAD1 > QRHEAD2;              // 强于大盘
QR2RESULT := QRHEAD1 < QRHEAD2;              // 弱于大盘
QR3RESULT := CROSS(QRHEAD1,QRHEAD2);         // 上穿（弱转强）
QR4RESULT := CROSS(QRHEAD2,QRHEAD1);         // 下穿（强转弱）
```
> `HLTEXPERTQRW` = 弘历专家强弱指标（dll 实现）。

### 2.3 背离王 BL（顶/底背离，含 ISDEPART）
```
BLHEAD1 := HLTEXPERTBLW(CLOSE,2,0,1);        // 背离基础序列（弘历专家背离）
BLHEAD2 := EMA(BLHEAD1,2);
BLHEAD3 := BLHEAD2 >= REF(BLHEAD2,1);        // 状态：1=上行 0=下行
BL1RESULT := BLHEAD3=1  AND REF(BLHEAD3,1)=0;   // 底背离（下转上）
BL2RESULT := BLHEAD3=0  AND REF(BLHEAD3,1)=1;   // 顶背离（上转下）
BL3RESULT := ISDEPART(BLHEAD2,2,%d);         // 底背离（指标ISDEPART, dir=2）
BL4RESULT := ISDEPART(BLHEAD2,1,%d);         // 顶背离（指标ISDEPART, dir=1）
```
> `HLTEXPERTBLW` = 弘历专家背离；`ISDEPART` = 背离算子（中源问鼎 dll 实现）。

### 2.4 箱体王 XT
```
XTHEAD1 := XTWBREAK(3);   // 突破上箱体
XTHEAD2 := XTWBREAK(4);   // 突破下箱体
XT1RESULT := XTHEAD1=1;   // 突破上箱体
XT2RESULT := XTHEAD2=1;   // 突破下箱体
```
> `XTWBREAK` = 箱体突破算子（dll 实现，参数 3=上 4=下）。

### 2.5 多空王 DK（空翻多 / 多翻空）
```
DKWHEAD1 := (3*C+L+O+H)/6;                  // 加权价
DKWHEAD2 := (20*DKWHEAD1 + 19*REF(DKWHEAD1,1) + ... + REF(DKWHEAD1,20))/210;  // 20日加权MA
DKWHEAD3 := MA(DKWHEAD2,15);
DK1RESULT := CROSS(DKWHEAD2,DKWHEAD3);      // 空翻多（短线穿长线向上）
DK2RESULT := CROSS(DKWHEAD3,DKWHEAD2);      // 多翻空（向下）
```

### 2.6 操盘王 CP（买入/卖出信号）
```
CPHEAD1 := (EMA((O+H+L+C)/4,3)+EMA(..,6)+EMA(..,9))/4;     // 快线
CPHEAD2 := (EMA((O+H+L+C)/4,5)+EMA(..,10)+EMA(..,20))/4;   // 慢线
CP1RESULT := CROSS(CPHEAD1,CPHEAD2);        // 买入信号（快穿慢）
CP2RESULT := CROSS(CPHEAD2,CPHEAD1);        // 卖出信号（慢穿快）
```

### 2.7 波段王 BD（绿变红 / 红变绿）
```
BDHEAD1 := (3*CLOSE+OPEN+HIGH+LOW)/6;
BDHEAD2 := FORCAST(EMA(BDHEAD1,8),6);       // 短期回归预测
BDHEAD3 := FORCAST(EMA(BDHEAD1,17),6);      // 长期回归预测
BDHEAD4 := BDHEAD2 >= BDHEAD3;             // 状态
BD1RESULT := BDHEAD4=1 AND REF(BDHEAD4,1)=0;   // 波段绿变红
BD2RESULT := BDHEAD4=0 AND REF(BDHEAD4,1)=1;   // 波段红变绿
```
> `FORCAST` = 线性回归预测（通达信内置）。

### 2.8 趋势王 WANG（主线/柱线 绿变红 红变绿）
```
WANGHEAD1 := FORCAST(EMA((3*C+2*O+H+L)/7,3),6);   // 主线预测
WANGHEAD2 := (O+H+L+C)/4;                          // 典型价
WANGHEAD3 := (EMA(WANGHEAD2,21)+EMA(WANGHEAD2,34)+EMA(WANGHEAD2,68))/3;  // 趋势线(21/34/68)
WANGHEAD4 := WANGHEAD3 > REF(WANGHEAD3,1);         // 趋势上行
WANGHEAD5 := WANGHEAD1 > REF(WANGHEAD1,1);         // 主线上行
WANG1RESULT := WANGHEAD5=1 AND REF(WANGHEAD5,1)=0; // 柱线绿变红
WANG2RESULT := WANGHEAD5=0 AND REF(WANGHEAD5,1)=1; // 柱线红变绿
WANG3RESULT := WANGHEAD4=1 AND REF(WANGHEAD4,1)=0; // 主线绿变红
WANG4RESULT := WANGHEAD4=0 AND REF(WANGHEAD4,1)=1; // 主线红变绿
```

---

## 3. 与截图的映射
| 截图分组 | 子条件 | 对应本文件 |
|---|---|---|
| 趋势王 | 柱线绿变红/红变绿 主线绿变红/红变绿 | WANG1-4 |
| 背离王 | 底背离/顶背离 | BL1-4 (含 ISDEPART) |
| 波段王 | 波段绿变红/红变绿 | BD1-2 |
| 操盘王 | 买入/卖出信号 | CP1-2 |
| 多空王 | 空翻多/多翻空 | DK1-2 |
| 箱体王 | 突破上/下箱体 | XT1-2 |
| 换手王 | 强于大盘/弱于大盘/飘带绿红 | HS1-2 (HSHEAD 换手率) |
| 强弱王 | 强弱 | QR1-4 |

## 4. 原始提取
- `_archive/hllevel2_badawang_raw.txt`（122 formula tokens）

## 5. 置信度
- **铁证（100% 逆）**：本文件全部公式来自 HLLevel2.EXE `.rdata` 明文常量。
- 各 HEAD 引用的 dll 算子：`HLTEXPERTQRW`/`HLTEXPERTBLW`/`XTWBREAK`/`HLTHBQONLYDATA`/`ISDEPART` 实现位于弘历系 dll（预测大师配套 dll，未在此 EXE 内联）。
