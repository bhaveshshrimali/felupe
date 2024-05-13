# -*- coding: utf-8 -*-
"""
This file is part of FElupe.

FElupe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FElupe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with FElupe.  If not, see <http://www.gnu.org/licenses/>.
"""
from .microsphere import affine_stretch_statevars
from tensortrax.math import array, abs as tensor_abs, maximum, sqrt, exp, if_else, real_to_dual
from tensortrax.math.special import try_stack, from_triu_1d, triu_1d, sym, dev
from tensortrax.math.linalg import det, inv, eigvalsh, expm


def morph(C, statevars, p):
    """Strain energy function of the
    `MORPH <https://doi.org/10.1016/s0749-6419(02)00091-8>`_ model formulation [1]_.

    Parameters
    ----------
    C : tensortrax.Tensor
        Right Cauchy-Green deformation tensor.
    statevars : array
        Vector of stacked state variables (CTS, C, SA).
    p : list of float
        A list which contains the 8 material parameters.

    Examples
    --------
    ..  pyvista-plot::
        :context:

        >>> import felupe as fem
        >>>
        >>> umat = fem.Hyperelastic(
        ...     fem.morph,
        ...     p=[0.039, 0.371, 0.174, 2.41, 0.0094, 6.84, 5.65, 0.244],
        ...     nstatevars=13,
        ... )
        >>> ax = umat.plot(
        ...    incompressible=True,
        ...    ux=fem.math.linsteps(
        ...        [1, 2, 1, 2.75, 1, 3.5, 1, 4.2, 1, 4.8, 1, 4.8, 1],
        ...        num=50,
        ...    ),
        ...    ps=None,
        ...    bx=None,
        ... )

    ..  pyvista-plot::
        :include-source: False
        :context:
        :force_static:

        >>> import pyvista as pv
        >>>
        >>> fig = ax.get_figure()
        >>> chart = pv.ChartMPL(fig)
        >>> chart.show()

    References
    ----------
    .. [1] D. Besdo and J. Ihlemann, "A phenomenological constitutive model for
       rubberlike materials and its numerical applications", International Journal
       of Plasticity, vol. 19, no. 7. Elsevier BV, pp. 1019–1036, Jul. 2003. doi:
       `10.1016/s0749-6419(02)00091-8 <https://doi.org/10.1016/s0749-6419(02)00091-8>`_.
    """

    # extract old state variables
    CTSn = array(statevars[0], like=C[0, 0])
    Cn = from_triu_1d(statevars[1:7], like=C)
    SAn = from_triu_1d(statevars[7:], like=C)

    # distortional part of right Cauchy-Green deformation tensor
    I3 = det(C)
    CG = C * I3 ** (-1 / 3)

    # inverse of and incremental right Cauchy-Green deformation tensor
    invC = inv(C)
    dC = C - Cn

    # eigenvalues of right Cauchy-Green deformation tensor (sorted in ascending order)
    λCG = eigvalsh(CG)

    # Tresca invariant of distortional part of right Cauchy-Green deformation tensor
    CTG = λCG[-1] - λCG[0]

    # maximum Tresca invariant in load history
    CTS = maximum(CTG, CTSn)

    def sigmoid(x):
        "Algebraic sigmoid function."
        return 1 / sqrt(1 + x**2)

    # material parameters
    α = p[0] + p[1] * sigmoid(p[2] * CTS)
    β = p[3] * sigmoid(p[2] * CTS)
    γ = p[4] * CTS * (1 - sigmoid(CTS / p[5]))

    LG = sym(dev(invC @ dC)) @ CG
    λLG = eigvalsh(LG)
    LTG = λLG[-1] - λLG[0]
    LG_LTG = if_else(LTG > 0, LG / LTG, LG)

    # limiting stresses "L" and additional stresses "A"
    SL = (γ * expm(p[6] * LG_LTG * CTG / CTS) + p[7] * LG_LTG) @ invC
    SA = (SAn + β * LTG * SL) / (1 + β * LTG)

    # second Piola-Kirchhoff stress tensor
    dψdC = (2 * α * dev(CG) @ invC + dev(SA @ C) @ invC) / 2
    statevars_new = try_stack([[CTS], triu_1d(C), triu_1d(SA)], fallback=statevars)

    return real_to_dual(dψdC, C), statevars_new


def morph_representative_directions(C, statevars, p, ε=1e-8):
    """Strain energy function of the
    `MORPH <https://doi.org/10.1016/s0749-6419(02)00091-8>`_ model formulation [1]_,
    implemented by the concept of
    `representative directions <https://nbn-resolving.org/urn:nbn:de:bsz:ch1-qucosa-114428>`_
    [2]_, [3]_.

    Parameters
    ----------
    C : tensortrax.Tensor
        Right Cauchy-Green deformation tensor.
    statevars : array
        Vector of stacked state variables (CTS, λ - 1, SA1, SA2).
    p : list of float
        A list which contains the 8 material parameters.
    ε : float, optional
        A small stabilization parameter (default is 1e-8).

    Examples
    --------
    ..  pyvista-plot::
        :context:

        >>> import felupe as fem
        >>>
        >>> umat = fem.Hyperelastic(
        ...     fem.morph_representative_directions,
        ...     p=[0.011, 0.408, 0.421, 6.85, 0.0056, 5.54, 5.84, 0.117],
        ...     nstatevars=84,
        ... )
        >>> ax = umat.plot(
        ...    incompressible=True,
        ...    ux=fem.math.linsteps(
        ...        [1, 2, 1, 2.75, 1, 3.5, 1, 4.2, 1, 4.8, 1, 4.8, 1],
        ...        num=50,
        ...    ),
        ...    ps=None,
        ...    bx=None,
        ... )

    ..  pyvista-plot::
        :include-source: False
        :context:
        :force_static:

        >>> import pyvista as pv
        >>>
        >>> fig = ax.get_figure()
        >>> chart = pv.ChartMPL(fig)
        >>> chart.show()

    References
    ----------
    .. [1] D. Besdo and J. Ihlemann, "A phenomenological constitutive model for
       rubberlike materials and its numerical applications", International Journal
       of Plasticity, vol. 19, no. 7. Elsevier BV, pp. 1019–1036, Jul. 2003. doi:
       `10.1016/s0749-6419(02)00091-8 <https://doi.org/10.1016/s0749-6419(02)00091-8>`_.

    .. [2] M. Freund, "Verallgemeinerung eindimensionaler Materialmodelle für die
       Finite-Elemente-Methode", Dissertation, Technische Universität Chemnitz,
       Chemnitz, 2013.

    .. [3] C. Miehe, S. Göktepe and F. Lulei, "A micro-macro approach to rubber-like
       materials - Part I: the non-affine micro-sphere model of rubber elasticity",
       Journal of the Mechanics and Physics of Solids, vol. 52, no. 11. Elsevier BV, pp.
       2617–2660, Nov. 2004. doi:
       `10.1016/j.jmps.2004.03.011 <https://doi.org/10.1016/j.jmps.2004.03.011>`_.
    """

    def morph_uniaxial(λ, statevars, p, ε=1e-8):
        """Return the force (per undeformed area) for a given longitudinal stretch in
        uniaxial incompressible tension or compression for the MORPH material
        formulation [1]_, [2]_.

        Parameters
        ----------
        λ : tensortrax.Tensor
            Longitudinal stretch of uniaxial incompressible deformation.
        statevars : array
            Vector of stacked state variables (CTS, λ - 1, SA1, SA2).
        p : list of float
            A list which contains the 8 material parameters.
        ε : float, optional
            A small stabilization parameter (default is 1e-8).

        References
        ----------
        .. [1] D. Besdo and J. Ihlemann, "A phenomenological constitutive model for
           rubberlike materials and its numerical applications", International Journal
           of Plasticity, vol. 19, no. 7. Elsevier BV, pp. 1019–1036, Jul. 2003. doi:
           `10.1016/s0749-6419(02)00091-8 <https://doi.org/10.1016/s0749-6419(02)00091-8>`_.

        .. [2] M. Freund, "Verallgemeinerung eindimensionaler Materialmodelle für die
           Finite-Elemente-Methode", Dissertation, Technische Universität Chemnitz,
           Chemnitz, 2013.

        """
        CTSn = array(statevars[:21], like=C, shape=(21,))
        λn = array(statevars[21:42], like=C, shape=(21,)) + 1
        SA1n = array(statevars[42:63], like=C, shape=(21,))
        SA2n = array(statevars[63:], like=C, shape=(21,))

        CT = tensor_abs(λ**2 - 1 / λ)
        CTS = maximum(CT, CTSn)

        L1 = 2 * (λ**3 / λn - λn**2) / 3
        L2 = (λn**2 / λ**3 - 1 / λn) / 3
        LT = tensor_abs(L1 - L2)

        sigmoid = lambda x: 1 / sqrt(1 + x**2)
        α = p[0] + p[1] * sigmoid(p[2] * CTS)
        β = p[3] * sigmoid(p[2] * CTS)
        γ = p[4] * CTS * (1 - sigmoid(CTS / p[5]))

        L1_LT = L1 / (ε + LT)
        L2_LT = L2 / (ε + LT)
        CT_CTS = CT / (ε + CTS)

        SL1 = (γ * exp(p[6] * L1_LT * CT_CTS) + p[7] * L1_LT) / λ**2
        SL2 = (γ * exp(p[6] * L2_LT * CT_CTS) + p[7] * L2_LT) * λ

        SA1 = (SA1n + β * LT * SL1) / (1 + β * LT)
        SA2 = (SA2n + β * LT * SL2) / (1 + β * LT)

        dψdλ = (2 * α + SA1) * λ - (2 * α + SA2) / λ**2
        statevars_new = try_stack([CTS, (λ - 1), SA1, SA2], fallback=statevars)

        return 5 * dψdλ.real_to_dual(λ), statevars_new

    return affine_stretch_statevars(
        C, statevars, f=morph_uniaxial, kwargs={"p": p, "ε": ε}
    )
