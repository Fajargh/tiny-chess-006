import sys
sys.path.insert(0, '.')
import engine as E

def test_mate(fen, maxd, label):
    E.load(fen)
    E.LM = 200000
    E.ND = 0
    # find best mating move from root (our turn, S==0)
    best = None
    bestd = 999
    for m in E.srt(E.gen(False), 0, 0):
        u = E.do(m)
        if E.atk(E.KS[1 - E.S], E.S == 0):
            E.undo(m, u)
            continue
        v = E.mt(maxd, 1)
        E.undo(m, u)
        if v < bestd:
            bestd = v
            best = m
    print(f"{label}: best mate distance={bestd} move={E.uci(best) if best else None} nodes={E.ND}")

# Mate in 1: white queen mates on back rank (black king a8, white Qd8# would need support; use a simple one)
# Fool's mate style: white to move, Qh5# is not mate. Use a real mate-in-1:
# White: Kg1, Qd5 ; Black: Ka8. Qd8# (queen to d8 is mate if supported... actually Qd8+ Ka8xb8? no)
# Simple back-rank: black king e8, white rook e1... let me use a known mate-in-1:
# White Q on h7, black K on h8, white K on g6: Qg7# (queen to g7 is mate)
test_mate("7k/7Q/6K1/8/8/8/8/8 w - - 0 1", 5, "mate-in-1 Qg7")
# KQ vs K: white K e6, Q d5, black K e8. Should find a mate within ~10 plies.
test_mate("4k3/8/4K3/3Q4/8/8/8/8 w - - 0 1", 13, "KQ vs K (Qd5)")
# No mate: starting position, should be 999
test_mate("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 9, "startpos (no mate)")
# KR vs K: white K e6, R d5, black K e8.
test_mate("4k3/8/4K3/3R4/8/8/8/8 w - - 0 1", 13, "KR vs K (Rd5)")
