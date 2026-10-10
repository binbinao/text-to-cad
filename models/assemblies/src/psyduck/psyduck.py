"""Psyduck figurine, ~120 mm tall, both hands pressed to its head.

Fresh design authored from the user brief. No geometry from any other model in
``models/`` is imported or referenced.

Coordinates
-----------
* +Z up; Z=0 is the ground plane the feet rest on
* +Y is the direction the figure faces
* +X is the figure's own left

This is a posed sculpture, not a mechanism, so the export is a labeled
multi-body compound: head, body, limbs, bill, eyes and plumes stay separate
closed solids with their own colours rather than being fused into one body.
"""

from __future__ import annotations
from cadgen import step

from math import sin, pi
from typing import Sequence

from cadgen import build123d as bd
from cadgen.assembly import label_shape

Point = tuple[float, float, float]
Vec = tuple[float, float, float]

# Linear RGBA. Plain tuples, not bd.Color: a module-level bd.Color would import
# the CAD kernel before the freshness gate can skip an unchanged build.
DUCK_YELLOW = (0.941, 0.788, 0.231, 1.0)
BILL_ORANGE = (0.886, 0.596, 0.216, 1.0)
BELLY_CREAM = (0.972, 0.925, 0.760, 1.0)
BLUSH_ROSE = (0.906, 0.502, 0.415, 1.0)
PLUME_DARK = (0.216, 0.176, 0.141, 1.0)
SCLERA_WHITE = (0.976, 0.973, 0.960, 1.0)
PUPIL_BLACK = (0.086, 0.078, 0.071, 1.0)

MIN_VOLUME = 1.0e-4

# --- the figure, in millimetres --------------------------------------------
HEAD_CENTER: Point = (0.0, 0.0, 74.0)
HEAD_RADII: Vec = (31.0, 29.0, 30.0)
BODY_CENTER: Point = (0.0, 0.0, 38.0)
BODY_RADII: Vec = (24.0, 22.0, 21.0)
# How far a colour patch stands proud of the surface it sits on, as a ratio.
PATCH_GROW = 1.022


# ---------------------------------------------------------------------------
# Small vector helpers for the lofts.
# ---------------------------------------------------------------------------

def _add(a: Point, b: Vec) -> Point:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Point, b: Point) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mul(v: Vec, k: float) -> Vec:
    return (v[0] * k, v[1] * k, v[2] * k)


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _length(v: Vec) -> float:
    return _dot(v, v) ** 0.5


def _unit(v: Vec) -> Vec:
    n = _length(v)
    if n < 1e-9:
        raise ValueError("Cannot normalise a zero vector")
    return _mul(v, 1.0 / n)


def _lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def _plane(origin: Point, axis: Vec, x_hint: Vec) -> bd.Plane:
    """A section plane at `origin` whose normal is `axis`."""
    z_dir = _unit(axis)
    hint = _unit(x_hint)
    projected = _sub(hint, _mul(z_dir, _dot(hint, z_dir)))
    if _length(projected) < 1e-6:
        hint = (0.0, 1.0, 0.0)
        projected = _sub(hint, _mul(z_dir, _dot(hint, z_dir)))
    x_dir = _unit(projected)
    return bd.Plane(origin=origin, x_dir=x_dir, z_dir=z_dir)


# ---------------------------------------------------------------------------
# Shape primitives.
# ---------------------------------------------------------------------------

def _ellipsoid_shape(center: Point, radii: Sequence[float]):
    """A true ellipsoid: build123d scales a unit sphere non-uniformly."""
    return bd.Sphere(1.0).scale(tuple(radii)).moved(bd.Location(center))


def _ellipsoid(center: Point, radii: Sequence[float], *, label: str, color) -> object:
    solid = _ellipsoid_shape(center, radii)
    if not solid.is_valid:
        raise ValueError(f"Ellipsoid {label!r} is invalid")
    return label_shape(solid, label, color=color)


def _loft(
    profiles: Sequence[tuple[Point, float, float]],
    *,
    axis: Vec,
    x_hint: Vec,
    label: str,
    color,
) -> object:
    """Loft elliptic sections; each entry is (origin, radius_along_x, radius_along_y)."""
    if len(profiles) < 2:
        raise ValueError(f"Loft {label!r} needs at least two sections")
    if any(rx <= 0.0 or ry <= 0.0 for _, rx, ry in profiles):
        raise ValueError(f"Loft {label!r} has a non-positive section radius")
    with bd.BuildPart() as body:
        for origin, radius_x, radius_y in profiles:
            with bd.BuildSketch(_plane(origin, axis, x_hint)):
                bd.Ellipse(radius_x, radius_y)
        bd.loft(ruled=False)
    if not body.part.is_valid or body.part.volume <= MIN_VOLUME:
        raise ValueError(f"Loft {label!r} is invalid")
    return label_shape(body.part, label, color=color)


def _member(
    start: Point,
    end: Point,
    start_radii: tuple[float, float],
    end_radii: tuple[float, float],
    *,
    label: str,
    color,
    x_hint: Vec = (1.0, 0.0, 0.0),
    curve: Vec = (0.0, 0.0, 0.0),
    bulge: float = 1.0,
) -> object:
    """A rounded limb: elliptic sections lofted along a bowed centre line.

    `curve` displaces the midpoint so a limb can bend; `bulge` fattens the
    middle the way a joint or a muscle does.
    """
    axis = _sub(end, start)
    profiles: list[tuple[Point, float, float]] = []
    for t in (0.0, 0.20, 0.50, 0.78, 1.0):
        bow = sin(pi * t)
        origin = _add(_lerp(start, end, t), _mul(curve, bow))
        rx = start_radii[0] + (end_radii[0] - start_radii[0]) * t
        ry = start_radii[1] + (end_radii[1] - start_radii[1]) * t
        gain = 1.0 + (bulge - 1.0) * bow
        profiles.append((origin, rx * gain, ry * gain))
    return _loft(profiles, axis=axis, x_hint=x_hint, label=label, color=color)


def _surface_patch(
    host_center: Point,
    host_radii: Sequence[float],
    limiter_center: Point,
    limiter_radii: Sequence[float],
    *,
    label: str,
    color,
) -> object:
    """A thin colour patch that hugs a host ellipsoid.

    The shell between the host and a slightly grown copy of it, clipped to the
    limiter. A patch modelled as a separate lens would either float off the
    curved surface or sink into it; this conforms by construction.
    """
    host = _ellipsoid_shape(host_center, host_radii)
    grown = _ellipsoid_shape(host_center, [r * PATCH_GROW for r in host_radii])
    limiter = _ellipsoid_shape(limiter_center, limiter_radii)
    patch = (grown & limiter) - host
    if not patch.is_valid or patch.volume <= MIN_VOLUME:
        raise ValueError(f"Surface patch {label!r} is invalid")
    return label_shape(patch, label, color=color)


def _mirrored(shape, *, label: str, color):
    return label_shape(bd.mirror(shape, about=bd.Plane.YZ), label, color=color)


# ---------------------------------------------------------------------------
# The figure. Every right-hand part is built once and mirrored across YZ, so
# the pose stays symmetric by construction rather than by duplicated numbers.
# ---------------------------------------------------------------------------

def build_psyduck():
    parts: list = []

    # --- head and body -----------------------------------------------------
    parts.append(_ellipsoid(HEAD_CENTER, HEAD_RADII, label="head", color=DUCK_YELLOW))
    parts.append(_ellipsoid(BODY_CENTER, BODY_RADII, label="body", color=DUCK_YELLOW))

    # --- legs and feet -----------------------------------------------------
    leg = _member(
        (11.0, 1.0, 26.0), (11.0, 4.0, 8.0), (10.0, 9.5), (8.0, 7.5),
        label="leg:right", color=DUCK_YELLOW, bulge=1.06,
    )
    parts.append(leg)
    parts.append(_mirrored(leg, label="leg:left", color=DUCK_YELLOW))

    foot = _ellipsoid((11.5, 6.0, 4.6), (11.5, 15.5, 4.6),
                      label="foot:right", color=DUCK_YELLOW)
    parts.append(foot)
    parts.append(_mirrored(foot, label="foot:left", color=DUCK_YELLOW))

    # --- bill: wide, flat, drooping slightly -------------------------------
    parts.append(_loft(
        (
            ((0.0, 18.0, 71.6), 17.5, 6.8),
            ((0.0, 28.0, 70.8), 17.8, 6.2),
            ((0.0, 37.0, 70.0), 17.2, 5.4),
            ((0.0, 43.5, 69.4), 15.0, 4.3),
            ((0.0, 47.0, 69.1), 9.5, 2.6),
            ((0.0, 48.5, 68.95), 3.5, 1.1),
        ),
        axis=(0.0, 1.0, 0.0), x_hint=(1.0, 0.0, 0.0),
        label="bill", color=BILL_ORANGE,
    ))

    # --- eyes: a bulging sclera with a pupil breaking its surface ----------
    sclera = _ellipsoid((10.0, 24.5, 84.0), (6.2, 5.2, 6.6),
                        label="eye_sclera:right", color=SCLERA_WHITE)
    parts.append(sclera)
    parts.append(_mirrored(sclera, label="eye_sclera:left", color=SCLERA_WHITE))

    pupil = _ellipsoid((10.3, 27.6, 83.6), (3.3, 3.1, 3.5),
                       label="eye_pupil:right", color=PUPIL_BLACK)
    parts.append(pupil)
    parts.append(_mirrored(pupil, label="eye_pupil:left", color=PUPIL_BLACK))

    # --- cheek blush: a patch conforming to the head -----------------------
    blush = _surface_patch(
        HEAD_CENTER, HEAD_RADII,
        (24.57, 21.85, 70.68), (9.5, 9.5, 9.5),
        label="cheek_blush:right", color=BLUSH_ROSE,
    )
    parts.append(blush)
    parts.append(_mirrored(blush, label="cheek_blush:left", color=BLUSH_ROSE))

    # --- belly patch --------------------------------------------------------
    parts.append(_surface_patch(
        BODY_CENTER, BODY_RADII,
        (0.0, 25.0, 38.0), (11.0, 9.5, 15.0),
        label="belly_patch", color=BELLY_CREAM,
    ))

    # --- arms raised to the head, the character's signature pose -----------
    # One bowed member per arm rather than upper/fore segments: two lofts
    # meeting at an elbow leave a lens-shaped seam that reads as a crease.
    arm = _member(
        (20.0, 0.0, 46.0), (25.5, 11.0, 86.5), (8.2, 7.8), (6.2, 6.0),
        label="arm:right", color=DUCK_YELLOW,
        curve=(6.0, -0.5, 3.0), bulge=1.10,
    )
    hand = _ellipsoid((25.5, 11.0, 86.5), (5.6, 6.6, 6.2),
                      label="hand:right", color=DUCK_YELLOW)
    for build, name in ((arm, "arm"), (hand, "hand")):
        parts.append(build)
        parts.append(_mirrored(build, label=f"{name}:left", color=DUCK_YELLOW))

    # --- three plumes on the crown ----------------------------------------
    right_plume = _member(
        (7.0, 4.0, 100.0), (10.0, -7.0, 115.0), (3.0, 2.6), (0.85, 0.85),
        label="plume:right", color=PLUME_DARK, curve=(2.5, -4.5, 0.5),
    )
    center_plume = _member(
        (0.0, 5.0, 101.5), (0.0, -7.0, 117.5), (3.2, 2.8), (0.85, 0.85),
        label="plume:center", color=PLUME_DARK, curve=(0.0, -5.5, 1.5),
    )
    parts.extend((right_plume, center_plume))
    parts.append(_mirrored(right_plume, label="plume:left", color=PLUME_DARK))

    # --- tail ---------------------------------------------------------------
    # Tapers to a near-point: a loft ends in a flat cap, and a stubby tail
    # ending in a visible disc reads as a hole rather than a tip.
    parts.append(_member(
        (0.0, -17.0, 32.0), (0.0, -27.0, 37.0), (8.0, 6.5), (1.2, 0.9),
        label="tail", color=DUCK_YELLOW, curve=(0.0, 0.0, -1.5), bulge=1.05,
    ))

    return bd.Compound(children=parts, label="psyduck")


@step(out="../../STEP/psyduck/psyduck.step")
def psyduck():
    return build_psyduck()


if __name__ == "__main__":
    psyduck()
