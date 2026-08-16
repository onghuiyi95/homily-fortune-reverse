"""Find registrars OTHER than FUN_10097040, decompile, grep for YDHYAD or garbled (encrypted) names.
The 261-name registrar (FUN_10097040) has NO YDHYAD. YDHYAD likely lives in another registrar
whose names may be encrypted (garbled), so plaintext find() misses it."""
import os, re, string
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
    print("total callers:", len(callers))
    found=False
    checked=0
    for ca in callers:
        if ca==0x10097040:  # skip known registrar
            continue
        cf=fm.getFunctionContaining(space.getAddress(ca))
        if cf is None:
            continue
        checked+=1
        res=decomp.decompileFunction(cf,150,mon)
        df=res.getDecompiledFunction()
        src=df.getC() if df else ''
        if 'YDHYAD' in src or 'ydhyad' in src.lower():
            print(f"FOUND YDHYAD in registrar @ {hex(ca)}")
            open(os.path.join(OUTDIR,f"_archive/tw_reg_found_{ca:x}.c"),"w").write(src)
            found=True
            break
        # look for garbled name strings (encrypted names would look non-clean)
        for m in re.finditer(r'FUN_10006480\(&stack0xffffffd0,"([^"]*)"\)', src):
            nm=m.group(1)
            if nm and not all(ch in string.ascii_letters+string.digits+'_' for ch in nm):
                if checked<=30:  # limit noise
                    print(f"  garbled in {hex(ca)}: {nm!r}")
        if checked>=40:
            print("...checked 40 registrars, stopping early")
            break
    if not found:
        print(f"YDHYAD NOT found in {checked} other registrars (checked up to limit)")
    print("done")
