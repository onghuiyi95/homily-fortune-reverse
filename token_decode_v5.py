# 完整通达信/弘历 公式 token -> 源码 解码器 v5
# 补全 token_decode_v4 未映射的 token，目标：解出完整可读源码（非中间表示）
# 已知 TDX 编码（基于 dll .rdata 函数名列表 + 公开 TDX token 文档）
import re

# 数据引用 (必达信标准)
DATA = {
    b'\x2b\x24\x27': 'CLOSE', b'\x2b\x24\x26': 'OPEN', b'\x2b\x24\x2d': 'HIGH',
    b'\x2b\x24\x2c': 'LOW', b'\x27\x24\x44': 'VOL', b'\x27\x24\x43': 'AMOUNT',
    b'\x2b\x24\x28': 'VOL',  # 量
}
# 多字节函数（通达信标准 token）
MULTI_FUNC = {
    b'\x40\x25': 'MA', b'\x3b\x3d\x25': 'SUM', b'\x21\x2e': 'IF',
    b'\x2d\x56\x3a': 'REF', b'\x52\x55': 'DMA', b'\x52\x54': 'HHV',
    b'\x52\x53': 'LLV', b'\x52\x51': 'MAX', b'\x52\x52': 'MIN',
    b'\x40\x1f': 'EMA', b'\x40\x22': 'SMA', b'\x3b\x3d\x29': 'COUNT',
    b'\x2d\x56\x3b': 'BARSLAST', b'\x52\x58': 'STD', b'\x52\x59': 'VAR',
    b'\x52\x56': 'ABS', b'\x52\x57': 'CROSS', b'\x52\x5a': 'LONGCROSS',
    b'\x52\x5b': 'TROUGH', b'\x52\x5c': 'PEAK', b'\x52\x5d': 'TROUGHBARS',
    b'\x52\x5e': 'PEAKBARS', b'\x52\x5f': 'WINNER', b'\x52\x60': 'COST',
    b'\x52\x61': 'BACKSET', b'\x52\x62': 'BARSCOUNT', b'\x52\x63': 'CURRBARSCOUNT',
    b'\x52\x64': 'TOTALBARSCOUNT', b'\x52\x65': 'BARSTATUS', b'\x52\x66': 'DATE',
    b'\x40\x3a': 'COS', b'\x40\x3b': 'SIN', b'\x40\x3c': 'TAN', b'\x40\x3d': 'EXP',
    b'\x40\x3e': 'LN', b'\x40\x3f': 'LOG', b'\x40\x40': 'SQRT', b'\x40\x41': 'POW',
    b'\x40\x42': 'CEILING', b'\x40\x43': 'FLOOR', b'\x40\x44': 'INTPART',
    b'\x40\x45': 'FRACPART', b'\x40\x46': 'REVERSE', b'\x40\x47': 'SIGN',
    b'\x40\x48': 'MAX', b'\x40\x49': 'MIN', b'\x40\x4a': 'MOD', b'\x40\x4b': 'RAND',
    b'\x40\x4c': 'AVEDEV', b'\x40\x4d': 'DEVSQ', b'\x40\x4e': 'FORCAST',
    b'\x40\x4f': 'SLOPE', b'\x40\x50': 'STD', b'\x40\x51': 'STDP', b'\x40\x52': 'VAR',
    b'\x40\x53': 'VARP', b'\x40\x54': 'COVAR', b'\x40\x55': 'RELATIVE',
    b'\x40\x56': 'MSE', b'\x40\x57': 'SKEW', b'\x40\x58': 'KURT', b'\x40\x59': 'CR',
}
# 运算符
MULTI_OP = {
    b'\x25\x29': '+', b'\x24\x21': '-', b'\x55\x27': '>', b'\x55\x24': '<',
    b'\x55\x26': '>=', b'\x55\x25': '<=', b'\x55\x28': '=', b'\x55\x29': '<>',
    b'\x43': '+', b'\x48': '*', b'\x47': '*', b'\x5c': '/', b'\x26': '/',
    b'\x21': '-', b'\x20': '-', b'\x4f': '+',
}
SINGLE = {0x39:'(',0x40:'(',0x29:'(',0x2b:'(',0x44:')',0x41:')',0x4a:')',
          0x42:':',0x3b:',',0x2e:',',0x45:',',0x3e:',',0x50:')',0x51:')',0x2c:','}
PARAM = {0x5b:'N1',0x5e:'N2',0x59:'N3',0x5a:'N4',0x5d:'N',0x5f:'N',0x58:'0',0x27:'N',0x56:'P1',0x57:'P2'}
INLINE = ['CURRENTTIME','BARSTATUS','BARSCOUNT','BUYVOL','ASKVOL','DECLINE','ADVANCE',
          'BACKSET','SELF','WINNER','COST','DMA','HHV','LLV','MAX','MIN','ADXD','YAD',
          'DYAD','DZADXD','YRU','DHEYDHXAD','DHXADXD','YDHYAD','HLT','IFMA','XTWBREAK',
          'ISDEPART','HLTHLP','HLTFDP','HLTHBQ']

def decode(tok):
    out=[]; i=0; n=len(tok)
    while i<n:
        b=tok[i]
        for mb,name in MULTI_FUNC.items():
            if tok[i:i+len(mb)]==mb: out.append(name); i+=len(mb); break
        else:
            for mb,name in DATA.items():
                if tok[i:i+len(mb)]==mb: out.append(name); i+=len(mb); break
            else:
                for mb,op in MULTI_OP.items():
                    if tok[i:i+len(mb)]==mb: out.append(op); i+=len(mb); break
                else:
                    if 0x41<=b<=0x5a:
                        m=re.match(rb'[A-Z][A-Z0-9]{1,15}',tok[i:])
                        if m:
                            nm=m.group(0).decode('latin1')
                            if nm in INLINE or len(nm)>=3:
                                out.append(nm); i+=len(m.group(0)); continue
                    if b in PARAM: out.append(PARAM[b]); i+=1; continue
                    if b in SINGLE: out.append(SINGLE[b]); i+=1; continue
                    if b==0x2d and i+1<n and 0x30<=tok[i+1]<=0x39:
                        out.append(chr(tok[i+1])); i+=2; continue
                    if b in (0x0c,0xeb,0x53,0x65,0x62,0xff): i+=1; continue
                    i+=1
    return ''.join(out)
