import sys, time, random
sys.path.insert(0, '/home/hatch/workspace/makefun/tiny-chess-v3')
import engine as E

def perft(depth):
    if depth == 0: return 1
    n = 0
    for m in E.gen(False):
        u = E.make(m)
        if not E.attacked(E.KS[1 - E.S], E.S == 0):
            n += perft(depth - 1)
        E.unmake(m, u)
    return n

def perft_caps(depth):
    if depth == 0: return 1
    n = 0
    for m in E.gen(True):
        u = E.make(m)
        if not E.attacked(E.KS[1 - E.S], E.S == 0):
            n += perft_caps(depth - 1)
        E.unmake(m, u)
    return n

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
POS3 = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POS4 = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
POS5 = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
POS6 = "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"

def test_perft():
    cases = [
        ("startpos", START, [20, 400, 8902, 197281, 4865609]),
        ("kiwipete", KIWIPETE, [48, 2039, 97862]),
        ("pos3", POS3, [14, 191, 2812, 43238, 674624]),
        ("pos4", POS4, [6, 264, 9467, 422333]),
        ("pos5", POS5, [44, 1486, 62379, 2103487]),
        ("pos6", POS6, [46, 2079, 89890, 3894594]),
    ]
    ok = True
    for name, fen, expect in cases:
        E.parse_fen(fen)
        for d, exp in enumerate(expect, 1):
            t0 = time.time()
            got = perft(d)
            dt = time.time() - t0
            status = "OK" if got == exp else "FAIL"
            if got != exp: ok = False
            print(f"perft {name} d{d}: {got} (exp {exp}) {status} {dt:.1f}s", flush=True)
            if got != exp: break
    return ok

def test_consistency():
    # incremental state (KEY, MG, EG, PH, PF, eval) must match a from-scratch
    # FEN rebuild, and a full make/unmake round-trip must restore startpos.
    rng = random.Random(42)
    ok = True
    for trial in range(200):
        E.parse_fen(START)
        stack = []
        for _ in range(30):
            legal = []
            for m in E.gen(False):
                u = E.make(m)
                if not E.attacked(E.KS[1 - E.S], E.S == 0):
                    legal.append(m)
                E.unmake(m, u)
            if not legal: break
            m = rng.choice(legal)
            u = E.make(m)
            stack.append((m, u))
        inc_key, inc_ev = E.KEY, E.ev_white()
        fen = E.current_fen()
        E.parse_fen(fen)
        if E.KEY != inc_key or E.ev_white() != inc_ev:
            print(f"trial {trial}: MISMATCH key {E.KEY} vs {inc_key}, ev {E.ev_white()} vs {inc_ev}")
            print("  fen:", fen)
            ok = False
            break
        E.parse_fen(START)
        k0 = E.KEY
        for m, u in stack:
            E.make(m)
        if E.KEY != inc_key:
            print(f"trial {trial}: replay key mismatch {E.KEY} vs {inc_key}")
            ok = False
            break
        for m, u in reversed(stack):
            E.unmake(m, u)
        if E.KEY != k0 or E.MG != 0 or E.EG != 0 or E.PH != 24:
            print(f"trial {trial}: ROUND-TRIP MISMATCH key {E.KEY} vs {k0}, MG={E.MG} EG={E.EG} PH={E.PH}")
            ok = False
            break
    print("eval/hash consistency:", "OK" if ok else "FAIL")
    return ok

def test_pesto_spot():
    # spot-check PeSTO orientation: white pawn on e2 vs e7, king on g1 vs e4.
    E.parse_fen("8/8/8/8/8/8/4P3/8 w - - 0 1")
    e2 = E.MG
    E.parse_fen("8/4P3/8/8/8/8/8/8 w - - 0 1")
    e7 = E.MG
    print(f"pawn MG e2={e2} e7={e7} (e7 should be much larger)")
    E.parse_fen("8/8/8/8/8/8/8/6K1 w - - 0 1")
    g1 = E.MG
    E.parse_fen("8/8/8/8/4K3/8/8/8 w - - 0 1")
    e4 = E.MG
    print(f"king MG g1={g1} e4={e4} (g1 should be larger in middlegame)")
    E.parse_fen("8/8/8/8/8/8/8/6K1 w - - 0 1")
    g1e = E.EG
    E.parse_fen("8/8/8/8/4K3/8/8/8 w - - 0 1")
    e4e = E.EG
    print(f"king EG g1={g1e} e4={e4e} (e4 should be larger in endgame)")
    return e7 > e2 and g1 > e4 and e4e > g1e

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ok = True
    if which in ("all", "perft"):
        ok &= test_perft()
    if which in ("all", "consistency"):
        ok &= test_consistency()
    if which in ("all", "pesto"):
        ok &= test_pesto_spot()
    print("ALL OK" if ok else "FAILURES PRESENT")
