#!/usr/bin/env python3
"""Tiny logistic regression without numpy (Newton steps, Gauss elimination). Used by the red-team scripts."""
import math


def solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            M[c][c] = 1e-12
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                if f:
                    for k in range(c, n + 1):
                        M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A)
    cols = []
    for j in range(n):
        e = [1.0 if i == j else 0.0 for i in range(n)]
        cols.append(solve(A, e))
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def fit(X, y, ridge=1e-4, iters=60):
    n, k = len(X), len(X[0])
    beta = [0.0] * k
    H = None
    for _ in range(iters):
        g = [0.0] * k
        H = [[ridge if i == j else 0.0 for j in range(k)] for i in range(k)]
        for xi, yi in zip(X, y):
            z = sum(b * v for b, v in zip(beta, xi))
            z = max(-30.0, min(30.0, z))
            p = 1.0 / (1.0 + math.exp(-z))
            w = p * (1 - p) + 1e-9
            for i in range(k):
                if xi[i] == 0.0:
                    continue
                g[i] += (yi - p) * xi[i]
                for j in range(k):
                    if xi[j] != 0.0:
                        H[i][j] += w * xi[i] * xi[j]
        step = solve(H, g)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-8:
            break
    cov = inverse(H)
    se = [math.sqrt(max(0.0, cov[i][i])) for i in range(k)]
    return beta, se


def predict(beta, x):
    z = max(-30.0, min(30.0, sum(b * v for b, v in zip(beta, x))))
    return 1.0 / (1.0 + math.exp(-z))
