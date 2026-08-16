"""Fix: decompile all registrars (callers of FUN_10006480) and grep for YDHYAD / encrypted names.
Address format from Ghidra is hex without 0x prefix (e.g. '1009a73e')."""
import os
DLL="C:/Turtle Winner/CompMan_chs.dll"
GHIDRA_DIR="C:/Users/Administrator/ai-shisho/_ghidra/ghidra_12.1.2_PUBLIC"
OUTDIR="C:/Users/Administrator/homily_fortune_reverse"
import pyghidra
pyghidra.start(install_dir=GHIDRA_DIR)
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.symbol import SourceType
with pyghidra.open_program(DLL, analyze=True) as api:
    program=api.getCurrentProgram()
    mon=ConsoleTaskMonitor()
    decomp=DecompInterface(); decomp.openProgram(program)
    fm=program.getFunctionManager()
    space=program.getAddressFactory().getDefaultAddressSpace()
    a=space.getAddress(0x10006480)
    refs=list(program.getReferenceManager().getReferencesTo(a))
    callers=sorted(set(int(str(ref.getFromAddress()),16) for ref in refs))
    print("num registrars:", len(callers))
    found=False
    for ca in callers:
        cf=fm.getFunctionContaining(space.getAddress(ca))
        if not cf: cf=fm.createFunction(space.getAddress(ca), SourceType.USER_DEFINED)
        res=decomp.decompileFunction(cf,200,mon)
        df=res.getDecompiledFunction()
        src=df.getC() if df else ''
        if 'YDHYAD' in src or 'ydhyad' in src.lower():
            print(f"FOUND YDHYAD in registrar @ {hex(ca)}")
            open(os.path.join(OUTDIR,f"_archive/tw_reg_found_{ca:x}.c"),"w").write(src)
            found=True
            break
        # also check for encrypted/garbled name strings (non-ascii-clean in FUN_10006480 calls)
        import re,string
        for m in re.finditer(r'FUN_10006480\(&stack0xffffffd0,"([^"]*)"\)', src):
            nm=m.group(1)
            if not all(ch in string.ascii_letters+string.digits+'_' for ch in nm):
                print(f"  garbled name in {hex(ca)}: {nm!r}")
                found=True
    if not found:
        print("YDHYAD NOT in any registrar; no garbled names either")
    print("done")
