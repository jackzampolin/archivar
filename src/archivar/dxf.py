"""DXF file loading and conversion utilities.

This module provides functions to load DXF files and convert them
to build123d geometry for 3D visualization and manipulation.
"""

from pathlib import Path
from typing import Union

import ezdxf
from ezdxf import recover
from ezdxf.entities import LWPolyline, Line, Arc, Circle, Spline
from build123d import (
    Face,
    Wire,
    Edge,
    Plane,
    Polyline as B3DPolyline,
    Line as B3DLine,
    ThreePointArc,
    Curve,
    make_face,
)
import math


def load_dxf(path: Union[str, Path]) -> ezdxf.document.Drawing:
    """Load a DXF file using ezdxf with recovery for potentially corrupted files.

    Args:
        path: Path to the DXF file

    Returns:
        ezdxf Drawing object
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DXF file not found: {path}")

    doc, auditor = recover.readfile(str(path))
    return doc


def get_entities(doc: ezdxf.document.Drawing) -> list:
    """Get all entities from the modelspace of a DXF document.

    Args:
        doc: ezdxf Drawing object

    Returns:
        List of DXF entities
    """
    msp = doc.modelspace()
    return list(msp)


def lwpolyline_to_points(entity: LWPolyline) -> list[tuple[float, float]]:
    """Convert an LWPolyline to a list of (x, y) points.

    Args:
        entity: LWPolyline entity from ezdxf

    Returns:
        List of (x, y) tuples
    """
    points = []
    for x, y, start_width, end_width, bulge in entity.get_points(format='xyseb'):
        points.append((x, y))

    if entity.closed and points and points[0] != points[-1]:
        points.append(points[0])

    return points


def dxf_to_edges(doc: ezdxf.document.Drawing) -> list[Edge]:
    """Convert DXF entities to build123d Edge objects.

    Supports: LWPolyline, Line, Circle, Arc

    Args:
        doc: ezdxf Drawing object

    Returns:
        List of build123d Edge objects
    """
    edges = []
    msp = doc.modelspace()

    for entity in msp:
        dxf_type = entity.dxftype()

        if dxf_type == 'LWPOLYLINE':
            points = lwpolyline_to_points(entity)
            if len(points) >= 2:
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i + 1]
                    if p1 != p2:
                        edge = Edge.make_line((*p1, 0), (*p2, 0))
                        edges.append(edge)

        elif dxf_type == 'LINE':
            start = (entity.dxf.start.x, entity.dxf.start.y, 0)
            end = (entity.dxf.end.x, entity.dxf.end.y, 0)
            if start != end:
                edges.append(Edge.make_line(start, end))

        elif dxf_type == 'CIRCLE':
            cx, cy = entity.dxf.center.x, entity.dxf.center.y
            radius = entity.dxf.radius
            # Create a plane at the circle center
            plane = Plane(origin=(cx, cy, 0))
            edges.append(Edge.make_circle(radius, plane=plane))

        elif dxf_type == 'ARC':
            center = (entity.dxf.center.x, entity.dxf.center.y, 0)
            radius = entity.dxf.radius
            start_angle = math.radians(entity.dxf.start_angle)
            end_angle = math.radians(entity.dxf.end_angle)

            # Calculate start and end points
            start_pt = (
                center[0] + radius * math.cos(start_angle),
                center[1] + radius * math.sin(start_angle),
                0
            )
            end_pt = (
                center[0] + radius * math.cos(end_angle),
                center[1] + radius * math.sin(end_angle),
                0
            )
            mid_angle = (start_angle + end_angle) / 2
            if end_angle < start_angle:
                mid_angle += math.pi
            mid_pt = (
                center[0] + radius * math.cos(mid_angle),
                center[1] + radius * math.sin(mid_angle),
                0
            )

            edges.append(Edge.make_three_point_arc(start_pt, mid_pt, end_pt))

    return edges


def dxf_to_face(path: Union[str, Path], tolerance: float = 0.1) -> Face:
    """Load a DXF file and convert it to a build123d Face.

    This is the main function for converting 2D DXF profiles to
    3D-ready geometry. The Face can then be extruded to create a solid.

    Args:
        path: Path to the DXF file
        tolerance: Tolerance for closing gaps in the wire (mm)

    Returns:
        build123d Face object
    """
    doc = load_dxf(path)
    edges = dxf_to_edges(doc)

    if not edges:
        raise ValueError(f"No convertible geometry found in {path}")

    # Build wire(s) from edges
    wires = Wire.combine(edges, tol=tolerance)

    # Ensure we have a list
    if not isinstance(wires, list):
        wires = [wires]

    if not wires:
        raise ValueError(f"Could not form closed wires from edges in {path}")

    # Sort by area - largest is the outer boundary
    wires_with_area = []
    for w in wires:
        try:
            area = abs(Face(w).area)
            wires_with_area.append((w, area))
        except Exception:
            # Skip wires that can't form faces
            continue

    if not wires_with_area:
        raise ValueError(f"No valid faces could be formed from {path}")

    wires_with_area.sort(key=lambda x: x[1], reverse=True)

    # Create the outer face
    outer_wire = wires_with_area[0][0]
    outer_face = Face(outer_wire)

    # Subtract holes (inner wires) from the outer face
    if len(wires_with_area) > 1:
        for hole_wire, _ in wires_with_area[1:]:
            try:
                hole_face = Face(hole_wire)
                outer_face = outer_face - hole_face
            except Exception:
                # Skip holes that fail
                continue

    return outer_face


def extrude_dxf(path: Union[str, Path], thickness: float) -> "Solid":
    """Load a DXF and extrude it to a 3D solid.

    Args:
        path: Path to the DXF file
        thickness: Extrusion thickness in mm

    Returns:
        build123d Solid object
    """
    from build123d import extrude

    face = dxf_to_face(path)
    solid = extrude(face, thickness)
    return solid
