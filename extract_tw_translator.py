"""Decompile functions in Turtle Winner CompMan_chs.dll that reference the formula function-name
strings (REF/MA/HLTHLP/etc). The formula-token translator references these; decompiling it reveals
the token->name mapping table. Also dump the .rdata region around the name array to find any
parallel token table."""
import os
DLL="C:/Turtle Winner/CompMan_chs.dll"
GHIDRA_DIR="C:/Users/Administrator/ai-shisho/_ghidra/ghidra_12.1.2_PUBLIC"
OUTDIR="C:/Users/Administrator/homily_fortune_reverse"
import pyghidra
pyghidra.start(install_dir=GHIDRA_DIR)
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
with pyghidra.open_program(DLL, analyze=True) as api:
    program=api.getCurrentProgram()
    mon=ConsoleTaskMonitor()
    decomp=DecompInterface(); decomp.openProgram(program)
    fm=program.getFunctionManager()
    space=program.getAddressFactory().getDefaultAddressSpace()
    listing=program.getListing()
    name_set={'REF','MA','HLTHLP','HHV','LLV','CLOSE','HLTFDP','HLTCHIPS','HLTHBQ',
              'ISDEPART','WINNER','COST','BACKSET','DMA','SUM','EMA','SMA','ABS','CROSS','IF','BOLL','MACD','BIAS'}
    refs=[]
    it=listing.getDefinedData(True)
    while it.hasNext():
        d=it.next()
        try: s=str(d.getValue())
        except: continue
        if s in name_set:
            for r in program.getReferenceManager().getReferencesTo(d.getAddress()):
                refs.append((s, r.getFromAddress().getOffset()))
    print("xrefs:", len(refs))
    out=open(os.path.join(OUTDIR,"_archive/tw_formula_translator.txt"),"w",encoding="utf-8")
    seen=set()
    for nm,frm in refs:
        a=space.getAddress(frm)
        cf=fm.getFunctionContaining(a)
        if cf and cf.getName() not in seen:
            seen.add(cf.getName())
            res=decomp.decompileFunction(cf,500,mon)
            df=res.getDecompiledFunction()
            out.write(f"\n//==== xref {nm} -> {cf.getName()} @ {cf.getEntryPoint()} ====\n{df.getC() if df else 'DECOMP FAILED'}\n")
            print("decompiled", cf.getName())
    out.close()
    print("funcs:", seen)
