import threading

from SigmarsGarden import solve_game


def worker(s, stop_event, result_holder):
    res = solve_game(s)
    if stop_event.is_set():
        return
    stop_event.set()
    result_holder[0] = res


def solver(s, n_threads=4):
    stop_event = threading.Event()
    result_holder = [[]]

    threads = []
    for i in range(n_threads):
        t = threading.Thread(target=worker, args=(s, stop_event, result_holder))
        t.start()
        threads.append(t)

    stop_event.wait()
    winner = result_holder[0]

    for t in threads:
        t.join(timeout=0.001)

    return winner


if __name__ == "__main__":
    x = solver("F_S___AE_F___S_WWEQWVMSAC___EW_E_AMEFQ_W__A_EGFFWWE__F_IA_F___FVEQ_QQTM_SW_A___V_AA__VLRM__")
    print(list(x))
