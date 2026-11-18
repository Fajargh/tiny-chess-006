import sys, time, importlib.util
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name]=m
    spec.loader.exec_module(m); return m
V1 = load("v1", "/home/hatch/workspace/makefun/tiny-chess/engine.py")
V2 = load("v2", "/home/hatch/workspace/makefun/tiny-chess-v2/engine.py")
FENS = [
 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
 "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
 "r1bqkb1r/pppp1ppp/2n2n2/4p2p/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5",
 "rnbq1rk1/pp2ppbp/3p1np1/8/2PNP3/2N1BP2/PP2P1PP/R2QKB1R w KQ - 0 7",
 "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
]
for eng, name in ((V1,'v1'),(V2,'v2')):
    tot_nodes=0; tot_t=0
    for fen in FENS:
        legal=[]
        eng.parse_fen(fen)
        for m in eng.gen(False):
            u=eng.make(m)
            if not eng.attacked(eng.KS[1-eng.S], eng.S==0): legal.append(eng.uci_of(m))
            eng.unmake(m,u)
        t0=time.time()
        eng.choose(fen, legal, 60000, "bench")
        dt=time.time()-t0
        tot_nodes+=eng.NODES; tot_t+=dt
        print(f"{name} {fen[:20]:22s} nodes={eng.NODES} time={dt:.2f}s nps={eng.NODES/dt:.0f}", flush=True)
    print(f"{name} TOTAL nps={tot_nodes/tot_t:.0f}  60k/move ~ {60000/(tot_nodes/tot_t):.2f}s", flush=True)
