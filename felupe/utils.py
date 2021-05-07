# -*- coding: utf-8 -*-
"""
 _______  _______  ___      __   __  _______  _______ 
|       ||       ||   |    |  | |  ||       ||       |
|    ___||    ___||   |    |  | |  ||    _  ||    ___|
|   |___ |   |___ |   |    |  |_|  ||   |_| ||   |___ 
|    ___||    ___||   |___ |       ||    ___||    ___|
|   |    |   |___ |       ||       ||   |    |   |___ 
|___|    |_______||_______||_______||___|    |_______|

This file is part of felupe.

Felupe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Felupe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Felupe.  If not, see <http://www.gnu.org/licenses/>.

"""

from collections import namedtuple
from copy import deepcopy as copy

import numpy as np
from scipy.sparse import csr_matrix as sparsematrix
from scipy.interpolate import interp1d

import meshio

from .forms import IntegralFormMixed
from .solve import partition, solve
from .math import identity, grad, dot, transpose, eigvals, det, interpolate, norms
from .field import Field

from .doftools import apply, partition as dofpartition, extend as dofextend


def dofresiduals(region, r, rref, dof1=None):

    rx = r
    ry = rref

    ry[ry == 0] = np.nan

    rxy = rx / ry

    rxy[region.mesh.elements_per_node == 1] = rx[region.mesh.elements_per_node == 1]

    if dof1 is None:
        return rxy
    else:
        return rxy.ravel()[dof1]


def newtonrhapson(
    region, fields, u0ext, fun_f, fun_A, dof1, dof0, unstack, maxiter=20, tol=1e-6
):

    # extract fields
    # u, p, J = fields
    dV = region.dV

    # deformation gradient at integration points
    F = identity(grad(fields[0])) + grad(fields[0])

    # PK1 stress and elasticity matrix
    f = fun_f(F, *[interpolate(f) for f in fields[1:]])
    A = fun_A(F, *[interpolate(f) for f in fields[1:]])

    # assembly
    r = IntegralFormMixed(f, fields, dV).assemble().toarray()[:, 0]
    K = IntegralFormMixed(A, fields, dV).assemble()

    converged = False

    for iteration in range(maxiter):

        system = partition(fields, r, K, dof1, dof0)
        dfields = np.split(solve(*system, u0ext), unstack)

        if np.any(np.isnan(dfields[0])):
            break
        else:
            for field, dfield in zip(fields, dfields):
                field.add(dfield)

        # deformation gradient at integration points
        F = identity(grad(fields[0])) + grad(fields[0])

        # PK1 stress and elasticity matrix
        f = fun_f(F, *[interpolate(f) for f in fields[1:]])

        # residuals and stiffness matrix components
        r = IntegralFormMixed(f, fields, dV).assemble().toarray()[:, 0]

        rref = np.linalg.norm(r[dof0])
        if rref == 0:
            rref = 1
        norm_r = np.linalg.norm(r[dof1]) / rref
        norm_dfields = norms(dfields)

        info_r = f"#{iteration+1:2d}: |r|={norm_r:1.3e}"
        info_f = [f"(|δ{1+i}|={norm_f:1.3e})" for i, norm_f in enumerate(norm_dfields)]

        print(" ".join([info_r, *info_f]))

        if norm_r < tol:  # np.array(norm_fields).sum() +
            converged = True
            break
        else:
            # elasticity matrix
            A = fun_A(F, *[interpolate(f) for f in fields[1:]])

            # assembly of stiffness matrix components
            K = IntegralFormMixed(A, fields, dV).assemble()

    Result = namedtuple(
        "Result", ["fields", "r", "K", "F", "f", "A", "unstack", "converged"]
    )

    return Result(copy(fields), r, K, F, f, A, unstack, converged)


def incsolve(
    fields,
    region,
    f,
    A,
    bounds,
    move,
    boundary="move",
    filename="out",
    maxiter=8,
    tol=1e-6,
    parallel=True,
):

    res = []

    # dofs to dismiss and to keep
    dof0, dof1, unstack = dofpartition(fields, bounds)
    # solve newton iterations and save result
    for increment, move_t in enumerate(move):

        print(f"\nINCREMENT {increment+1:2d}   (move={move_t:1.3g})")
        # set new value on boundary
        bounds[boundary].value = move_t

        # obtain external displacements for prescribed dofs
        u0ext = apply(fields[0], bounds, dof0)

        Result = newtonrhapson(
            region, fields, u0ext, f, A, dof1, dof0, unstack, maxiter=maxiter, tol=tol
        )

        fields = Result.fields

        if not Result.converged:
            # reset counter for last converged increment and break
            increment = increment - 1
            break
        else:
            # save results and go to next increment
            res.append(Result)
            save(region, *Result, filename=filename)
            # save(region, *Result, filename=filename + f"_{increment+1:d}")
            print("SAVED TO FILE")

    savehistory(region, res, filename=filename)

    return res


def tonodes(values, region, sym=True, mode="tensor"):

    rows = region.mesh.connectivity.T.ravel()
    cols = np.zeros_like(rows)

    ndim = region.mesh.ndim

    if mode == "tensor":
        if sym:
            if ndim == 3:
                ij = [(0, 0), (1, 1), (2, 2), (0, 1), (1, 2), (0, 2)]
            elif ndim == 2:
                ij = [(0, 0), (1, 1), (0, 1)]
        else:
            if ndim == 3:
                ij = [
                    (0, 0),
                    (0, 1),
                    (0, 2),
                    (1, 0),
                    (1, 1),
                    (1, 2),
                    (2, 0),
                    (2, 1),
                    (2, 2),
                ]
            elif ndim == 2:
                ij = [(0, 0), (0, 1), (1, 0), (1, 1)]

        out = Field(region, dim=len(ij)).values

        for a, (i, j) in enumerate(ij):
            out[:, a] = (
                sparsematrix(
                    (values.reshape(ndim, ndim, -1)[i, j], (rows, cols)),
                    shape=(region.mesh.nnodes, 1),
                ).toarray()[:, 0]
                / region.mesh.elements_per_node
            )

    elif mode == "scalar":
        out = sparsematrix(
            (values.ravel(), (rows, cols)), shape=(region.mesh.nnodes, 1)
        ).toarray()[:, 0]
        out = out / region.mesh.elements_per_node

    return out


def save(
    region,
    fields,
    r,
    K=None,
    F=None,
    f=None,
    A=None,
    unstack=None,
    converged=True,
    filename="out",
):

    if unstack is not None:
        reactionforces = np.split(r, unstack)[0]
        u = fields[0]
        P = f[0]
    else:
        reactionforces = r
        u = fields
        P = f

    mesh = region.mesh

    point_data = {
        "Displacements": u.values,
        "ReactionForce": reactionforces.reshape(*u.values.shape),
    }

    if f is not None:
        # cauchy stress at integration points
        s = dot(P, transpose(F)) / det(F)
        sp = eigvals(s)

        # shift stresses to nodes and average nodal values
        cauchy = tonodes(s, region=region, sym=True)
        cauchyprinc = [tonodes(sp_i, region=region, mode="scalar") for sp_i in sp]

        point_data["CauchyStress"] = cauchy

        point_data["MaxPrincipalCauchyStress"] = cauchyprinc[2]
        point_data["IntPrincipalCauchyStress"] = cauchyprinc[1]
        point_data["MinPrincipalCauchyStress"] = cauchyprinc[0]

    mesh = meshio.Mesh(
        points=mesh.nodes,
        cells={mesh.etype: mesh.connectivity[:, : mesh.edgenodes]},
        # Optionally provide extra data on points, cells, etc.
        point_data=point_data,
    )
    
    mesh.write(filename + ".vtk")


def savehistory(region, results, filename="out"):

    mesh = region.mesh
    points = mesh.nodes
    cells = {mesh.etype: mesh.connectivity[:, : mesh.edgenodes]}

    with meshio.xdmf.TimeSeriesWriter(filename + ".xdmf") as writer:
        writer.write_points_cells(points, cells)

        for inc, result in enumerate(results):
            fields, r, K, F, f, A, unstack, converged = result

            if unstack is not None:
                reactionforces = np.split(r, unstack)[0]
            else:
                reactionforces = r

            u = fields[0]

            point_data = {
                "Displacements": u.values,
                "ReactionForce": reactionforces.reshape(*u.values.shape),
            }

            if f is not None:
                # cauchy stress at integration points
                s = dot(f[0], transpose(F)) / det(F)
                sp = eigvals(s)

                # shift stresses to nodes and average nodal values
                cauchy = tonodes(s, region=region, sym=True)
                cauchyprinc = [
                    tonodes(sp_i, region=region, mode="scalar") for sp_i in sp
                ]

                point_data["CauchyStress"] = cauchy

                point_data["MaxPrincipalCauchyStress"] = cauchyprinc[2]
                point_data["IntPrincipalCauchyStress"] = cauchyprinc[1]
                point_data["MinPrincipalCauchyStress"] = cauchyprinc[0]

            writer.write_data(inc, point_data=point_data)


def reactionforce(results, bounds, boundary="move"):
    return np.array(
        [
            (
                ((np.split(res.r, res.unstack)[0]).reshape(-1, 3))[
                    bounds[boundary].nodes
                ]
            ).sum(0)
            for res in results
        ]
    )


def curve(x, y):
    if len(y) > 1:
        kind = "linear"
    if len(y) > 2:
        kind = "quadratic"
    if len(y) > 3:
        kind = "cubic"

    f = interp1d(x[: len(y)], y, kind=kind)
    xx = np.linspace(x[0], x[: len(y)][-1])
    return (x[: len(y)], y), (xx, f(xx))
