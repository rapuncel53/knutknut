import time
import multiprocessing as mp
import numpy as np

xs = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4])
ys = np.array([4.03, 4.19, 4.26, 4.25, 4.17, 4.03, 3.85, 3.63, 3.40, 3.16, 2.93, 2.72, 2.53, 2.39, 2.28, 2.21, 2.18, 2.19, 2.22, 2.27, 2.33, 2.39, 2.44, 2.45, 2.43, 2.36, 2.22, 2.02, 1.75, 1.41, 1.00, 0.52, -0.01, -0.60, -1.22, -1.86, -2.50, -3.13, -3.72, -4.27, -4.75, -5.15, -5.45, -5.65, -5.74, -5.70, -5.55, -5.29, -4.92, -4.44, -3.89, -3.26, -2.58, -1.86, -1.12, -0.39, 0.32, 0.98, 1.60, 2.14, 2.61, 2.99, 3.28, 3.47, 3.57])

def predict(x, theta):
    return (theta[0]*np.sin(theta[1]*(x + theta[2])) +
            theta[3]*np.sin(theta[4]*(x + theta[5])) +
            theta[6]*np.sin(theta[7]*(x + theta[8])))

def get_loss(y_hat, ys):
    return ((y_hat - ys)**2).sum()

def worker_run(args):
    seed, n_iterations, n_params = args
    np.random.seed(seed)
    best_loss = float('inf')
    best_theta = None
    for _ in range(n_iterations):
        theta = np.random.uniform(-4, 4, size=n_params)
        loss = get_loss(predict(xs, theta), ys)
        if loss < best_loss:
            best_loss = loss
            best_theta = theta
    return best_loss, best_theta

def run_sequential(total_iterations=100000, n_params=9):
    t0 = time.time()
    best_loss, best_theta = worker_run((42, total_iterations, n_params))
    elapsed = time.time() - t0
    return elapsed, best_loss, best_theta

def run_multiprocess(num_workers=4, total_iterations=100000, n_params=9):
    iters_per_worker = total_iterations // num_workers
    tasks = [(42 + i, iters_per_worker, n_params) for i in range(num_workers)]
    t0 = time.time()
    with mp.Pool(num_workers) as pool:
        results = pool.map(worker_run, tasks)
    elapsed = time.time() - t0
    best_loss = min(r[0] for r in results)
    best_theta = min(results, key=lambda r: r[0])[1]
    return elapsed, best_loss, best_theta

if __name__ == '__main__':
    total_iters = 100000
    print(f"=== Fortuna Multiprocessing Benchmark (Total iterations: {total_iters}) ===")
    
    # Sequential (1 worker)
    t_seq, loss_seq, _ = run_sequential(total_iters)
    print(f"1 Process (Sequential): {t_seq:.3f} s, Best Loss: {loss_seq:.4f}")
    
    # Multiprocess with different worker counts
    for w in [2, 4, 8]:
        t_mp, loss_mp, _ = run_multiprocess(num_workers=w, total_iterations=total_iters)
        speedup = t_seq / t_mp
        efficiency = (speedup / w) * 100
        print(f"{w} Processes: {t_mp:.3f} s (Speedup: {speedup:.2f}x, Efficiency: {efficiency:.1f}%), Best Loss: {loss_mp:.4f}")
