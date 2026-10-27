"""Extension point for *inelastic* gamma-ray transport; intentionally unimplemented.

The Bethell elastic reverse-scattering estimator is not directly reusable for
Compton downscattering or pair production. A valid adjoint formulation needs
energy-dependent kernels, source terms, and correct reverse weights.
"""


def gamma_transport_not_implemented() -> None:
    raise NotImplementedError(
        "Gamma transport requires a separately designed and validated "
        "forward/adjoint energy-dependent transport model."
    )
