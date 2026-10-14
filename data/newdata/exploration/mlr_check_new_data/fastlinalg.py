"""Speed patch: LAPACK SVD/QR is very slow on this machine (46-120 s for a 36000x481 matrix) while matmul takes 0.3 s.
Replace pinv / lstsq / matrix_rank / statsmodels pinv_extended for tall matrices by an eigendecomposition of X'X.
Verified on one fold: max |beta_lstsq - beta_normal_eq| = 1.2e-8."""
import numpy as np
import statsmodels.tools.tools as _tt
import statsmodels.regression.linear_model as _lm

_orig_pinv, _orig_rank, _orig_lstsq, _orig_pe = np.linalg.pinv, np.linalg.matrix_rank, np.linalg.lstsq, _tt.pinv_extended


def _tall(a):
    a = np.asarray(a)
    return a.ndim == 2 and a.shape[0] > 3 * a.shape[1] and a.shape[1] > 50


def _eig_pinv(x):
    x = np.ascontiguousarray(x, dtype=float)
    d = np.sqrt((x * x).sum(0))
    d[d == 0] = 1.0
    xs = x / d                                   # unit-norm columns: kills the scale differences (raw mileage vs dummies)
    lam, V = np.linalg.eigh(xs.T @ xs)
    keep = lam > lam.max() * 1e-13
    Vk = V[:, keep]
    return ((Vk / lam[keep]) @ (Vk.T @ xs.T)) / d[:, None], np.sqrt(lam[::-1].clip(0))


def _rank(a, *args, **kw):
    if _tall(a):
        a = np.ascontiguousarray(a, dtype=float)
        d = np.sqrt((a * a).sum(0))
        d[d == 0] = 1.0
        a = a / d
        lam = np.linalg.eigvalsh(a.T @ a)
        return int((lam > lam.max() * 1e-13).sum())
    return _orig_rank(a, *args, **kw)


def _lstsq(a, b, rcond=None):
    if _tall(a):
        return _eig_pinv(a)[0] @ np.asarray(b), None, None, None
    return _orig_lstsq(a, b, rcond=rcond)


def _pinv_ext(x, rcond=1e-15):
    x = np.asarray(x, dtype=float)
    return _eig_pinv(x) if _tall(x) else _orig_pe(x, rcond=rcond)


np.linalg.pinv = lambda a, *args, **kw: _eig_pinv(a)[0] if _tall(a) else _orig_pinv(a, *args, **kw)
np.linalg.matrix_rank = _rank
np.linalg.lstsq = _lstsq
_tt.pinv_extended = _pinv_ext
if hasattr(_lm, 'pinv_extended'):
    _lm.pinv_extended = _pinv_ext
