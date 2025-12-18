#!/usr/bin/env python3
"""
Extract individual parts from Archivar DXF files.
Parts are stored as BLOCK definitions - this script extracts each block
to its own DXF file, organized into translated English folders.
"""

import ezdxf
from ezdxf import recover
from pathlib import Path
import re
from collections import defaultdict

# German to English translations for part names
TRANSLATIONS = {
    # Main structure parts
    'bildschirmplatte': 'screen_plate',
    'füße': 'feet',
    'fuße': 'feet',
    'seitenplatte': 'side_plate',
    'frontplatte': 'front_plate',
    'verstrebung': 'support_brace',
    'dose': 'lamp_housing',

    # Carriage (Wagen) parts
    'wagen_basis': 'carriage_base',
    'wagenbasis': 'carriage_base',
    'wagenflügel': 'carriage_wing',
    'wagenwinkel': 'carriage_angle',
    'seitenteil_wagen': 'carriage_side',
    'spanngriff': 'clamp_knob',
    'spannstück': 'clamp_piece',
    'spannhülse': 'clamp_sleeve',

    # Camera parts
    'kamerabefestigung': 'camera_mount',

    # Lever parts
    'hebel_kurz': 'short_lever',
    'hebel_lang': 'long_lever',

    # Lighting module parts
    'lampenplatte_unten': 'lamp_plate_bottom',
    'lampenplatte_mitte': 'lamp_plate_middle',
    'lampenplatte_oben': 'lamp_plate_top',
    'lampenführung': 'lamp_guide',
    'lampenbefestigung': 'lamp_mount',
    'dachplatte': 'roof_plate',
    'frontplatte_lichtmodul': 'light_module_front',
    'lichtmodul': 'light_module',
    'umlenkplatte_groß': 'deflector_large',
    'umlenkplatte_gross': 'deflector_large',
    'umlenkplatte_klein': 'deflector_small',
    'fenster': 'window',
    'plättchen': 'small_plate',
    'plattchen': 'small_plate',

    # Insert/filler parts (sandwich design)
    'holzeinlage_griff': 'handle_wood_insert',
    'holzflach_basisprofil_innen': 'base_profile_inner',
    'holzflach_wagenprofil_innen': 'carriage_profile_inner',

    # Directional terms
    'links': 'left',
    'rechts': 'right',
    'vorne': 'front',
    'hinten': 'rear',
    'mitte': 'middle',
    'groß': 'large',
    'gross': 'large',
    'klein': 'small',
    'kurz': 'short',
    'lang': 'long',
    'oben': 'top',
    'unten': 'bottom',
}

# Block name patterns to skip (system blocks, assembly references, hardware)
SKIP_PATTERNS = [
    r'^[\*_]',           # Anonymous/system blocks
    r'^Vordans\d+$',     # Style blocks
    r'^Archivar_',       # Assembly reference
    r'^Basis_',          # Assembly reference
    r'^Wagen_1_',        # Assembly reference
    r'^Bildmodul_',      # Assembly reference
    r'^Befestigung_',    # Assembly reference
    r'^Bildschirm_',     # Assembly reference
    r'^Hebel_links',     # Duplicate assembly ref (keep hebel_lang/kurz)
    r'^Hebel_rechts',    # Duplicate assembly ref
    r'^Spannstück_links',# Duplicate assembly ref (keep spannstück_wagen)
    r'^Spannstück_rechts',
    r'^Kamerabefestigung_rechts',  # Duplicate (keep kamerabefestigung_1)
    r'^Kamerabefestigung_links',
    r'^Wagenwinkel_links_vorne',   # Duplicate (keep wagenwinkel_links_202)
    r'^Wagenwinkel_rechts',
    r'^Seitenplatte_links',        # Duplicate (keep seitenplatte_1)
    r'^Seitenplatte_rechts',
    r'^Seitenteil_wagen_links',    # Duplicate (keep seitenteil_wagen)
    r'^Seitenteil_wagen_rechts',
    r'^Wagenflügel_links',         # Duplicate (keep wagenflügel_1)
    r'^Wagenflügel_rechts',
    r'^Verstrebung_links',         # Duplicate
    r'^Verstrebung_rechts',
    r'^Frontplatte_vorne',         # Duplicate (keep frontplatte_301)
    r'^Frontplatte_hinten',
    r'^Lichtmodul$',               # Assembly ref
    r'^Beleuchtung',               # Assembly ref
    # Hardware / fasteners (not laser cut parts)
    r'^scheibe_',                  # Washers
    r'^schraube_',                 # Screws
    r'^rändelschraube',            # Knurled screws
    r'^kugellager',                # Ball bearings
    r'^einschraubmuffe',           # Threaded inserts
    r'^höhenverstellschraube',     # Height adjustment screws
    r'^abdeckkappe',               # Cover caps
    r'^rohr$',                     # Tube (aluminum, not laser cut)
    r'^aluwinkel$',                # Aluminum angle (not laser cut)
    r'^basisprofil$',              # Base profile (aluminum)
    r'^wagenprofil$',              # Carriage profile (aluminum)
    r'^glas$',                     # Glass panes
    r'^filzstreifen',              # Felt strips
    r'^dichtprofil',               # Seal profiles
    r'^steckerleiste',             # Power strip
    r'^usb',                       # USB parts
    r'^federzug',                  # Spring pull
    r'^lampenfassung',             # Lamp socket
    r'^\d+_',                      # Part numbers like 70662_1_prt
    r'^bildschirm$',               # Screen (assembly reference)
    r'^glas$',                     # Glass (not laser cut)
    r'^aluwinkel$',                # Aluminum angle (not laser cut)
    r'^basisprofil$',              # Aluminum base profile
]


def should_skip_block(name: str) -> bool:
    """Check if block should be skipped."""
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True
    return False


def get_base_part_name(block_name: str) -> str:
    """Extract base part name from block name, removing instance numbers."""
    # Remove trailing __numbers
    name = re.sub(r'__\d+$', '', block_name)
    # Remove trailing _numbers
    name = re.sub(r'_\d+$', '', name)
    # Clean up double underscores
    name = re.sub(r'__+', '_', name)
    return name.lower()


def translate_name(german_name: str) -> str:
    """Translate German part name to English."""
    name = german_name.lower()

    # Remove instance numbers
    name = re.sub(r'_+\d+$', '', name)
    name = re.sub(r'__+', '_', name)

    # Remove thickness suffixes (like _8mm, _10mm) - they'll be in folder structure
    name = re.sub(r'_\d+mm$', '', name)

    # Try direct match
    if name in TRANSLATIONS:
        return TRANSLATIONS[name]

    # Try partial translations (longest first)
    result = name
    for german, english in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        result = result.replace(german, english)

    # Clean up
    result = re.sub(r'_+', '_', result)
    result = result.strip('_')

    # Remove any remaining thickness indicators
    result = re.sub(r'_\d+mm$', '', result)

    return result


def get_part_category(part_name: str) -> str:
    """Categorize part into a folder."""
    name = part_name.lower()

    # Lighting module parts (4mm)
    if any(x in name for x in ['lampenplatte', 'licht', 'fenster', 'dach',
                                'umlenkplatte', 'dose_1', 'plättchen', 'plattchen']):
        return '04_lighting_module'

    # Carriage parts
    if any(x in name for x in ['wagen', 'spann']):
        return '02_carriage'

    # Camera parts
    if 'kamera' in name:
        return '03_camera_mount'

    # Lamp housing / guide (main structure lamp arms)
    if 'dose' in name and 'dose_1' not in name:
        return '01_main_frame'

    # Base/frame parts
    if any(x in name for x in ['seiten', 'front', 'bildschirm', 'füße', 'fuße',
                               'verstrebung', 'hebel']):
        return '01_main_frame'

    # Profile inserts (sandwich design)
    if 'holz' in name:
        return '05_profile_inserts'

    return '06_other'


def count_real_entities(block) -> int:
    """Count actual geometry entities in block, not sub-references."""
    count = 0
    for entity in block:
        if entity.dxftype() in ('LINE', 'CIRCLE', 'ARC', 'LWPOLYLINE',
                                 'POLYLINE', 'SPLINE', 'ELLIPSE'):
            count += 1
    return count


def explode_block_to_entities(doc, block_name: str):
    """Get all entities from a block, exploding nested blocks."""
    entities = []

    def collect_entities(block, transform=None):
        for entity in block:
            if entity.dxftype() == 'INSERT':
                # Recursively explode nested blocks
                nested_block = doc.blocks.get(entity.dxf.name)
                if nested_block:
                    collect_entities(nested_block)
            else:
                entities.append(entity)

    block = doc.blocks.get(block_name)
    if block:
        collect_entities(block)

    return entities


def extract_block_to_dxf(doc, block_name: str, output_path: Path) -> int:
    """Extract a block's geometry to a new DXF file."""
    block = doc.blocks.get(block_name)
    if not block:
        return 0

    # Create new document
    target_doc = ezdxf.new('R2010')
    target_msp = target_doc.modelspace()

    # Recursively collect all geometry
    entity_count = 0

    def copy_entities(source_block):
        nonlocal entity_count
        for entity in source_block:
            if entity.dxftype() == 'INSERT':
                # Recursively process nested blocks
                nested = doc.blocks.get(entity.dxf.name)
                if nested and not entity.dxf.name.startswith('*'):
                    copy_entities(nested)
            elif entity.dxftype() in ('LINE', 'CIRCLE', 'ARC', 'LWPOLYLINE',
                                       'POLYLINE', 'SPLINE', 'ELLIPSE', 'POINT'):
                try:
                    new_entity = entity.copy()
                    target_msp.add_entity(new_entity)
                    entity_count += 1
                except Exception as e:
                    pass  # Skip problematic entities

    copy_entities(block)

    if entity_count > 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_doc.saveas(output_path)

    return entity_count


def process_dxf_file(dxf_path: Path, output_base: Path, thickness: str) -> dict:
    """Process a DXF file and extract all unique parts."""
    print(f"\nProcessing: {dxf_path.name}")
    print(f"  Thickness: {thickness}")

    try:
        doc, auditor = recover.readfile(str(dxf_path))
    except Exception as e:
        print(f"  Error loading: {e}")
        return {}

    # Find all blocks with geometry
    blocks_with_geometry = {}
    for block in doc.blocks:
        if block.name.startswith('*'):
            continue
        entity_count = count_real_entities(block)
        if entity_count > 0:
            blocks_with_geometry[block.name] = entity_count

    print(f"  Found {len(blocks_with_geometry)} blocks with geometry")

    # Group blocks by base part name
    parts_by_base = defaultdict(list)
    for block_name, count in blocks_with_geometry.items():
        if should_skip_block(block_name):
            continue
        base_name = get_base_part_name(block_name)
        parts_by_base[base_name].append((block_name, count))

    print(f"  Identified {len(parts_by_base)} unique parts")

    # Extract each unique part (use version with most entities)
    extracted = {}
    for base_name, instances in sorted(parts_by_base.items()):
        # Pick the instance with most entities
        best_block, best_count = max(instances, key=lambda x: x[1])

        # Translate and categorize
        english_name = translate_name(base_name)
        category = get_part_category(base_name)

        # Output path
        output_dir = output_base / category / thickness
        output_file = output_dir / f"{english_name}.dxf"

        # Extract
        actual_count = extract_block_to_dxf(doc, best_block, output_file)

        if actual_count > 0:
            extracted[english_name] = {
                'german': base_name,
                'block': best_block,
                'entities': actual_count,
                'category': category,
                'file': str(output_file.relative_to(output_base))
            }
            print(f"    {base_name} -> {english_name} ({actual_count} entities)")

    return extracted


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    cad_dir = project_dir / 'CAD'
    output_dir = project_dir / 'CAD' / 'individual_parts'

    # Clean output directory
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)

    print("=" * 60)
    print("Archivar DXF Part Extractor")
    print("=" * 60)
    print(f"Source: {cad_dir}")
    print(f"Output: {output_dir}")

    # Source files
    dxf_files = [
        (cad_dir / 'MainStructure18mmPlywood' / 'proto116_laser_18mm.dxf', '18mm'),
        (cad_dir / 'MainStructure18mmPlywood' / 'proto117_laser_8mm.dxf', '8mm'),
        (cad_dir / 'MainStructure18mmPlywood' / 'proto117_laser_10mm.dxf', '10mm'),
        (cad_dir / 'LightingModule4mmPlywood' / 'proto116_laserteile_4mm.dxf', '4mm'),
    ]

    all_parts = {}

    for dxf_path, thickness in dxf_files:
        if dxf_path.exists():
            parts = process_dxf_file(dxf_path, output_dir, thickness)
            all_parts[thickness] = parts
        else:
            print(f"\nWarning: File not found: {dxf_path}")

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)

    total = sum(len(p) for p in all_parts.values())
    print(f"Total unique parts extracted: {total}")

    print("\nFolder structure:")
    if output_dir.exists():
        for category in sorted(output_dir.iterdir()):
            if category.is_dir():
                print(f"\n  {category.name}/")
                for thickness_dir in sorted(category.iterdir()):
                    if thickness_dir.is_dir():
                        files = sorted(thickness_dir.glob('*.dxf'))
                        print(f"    {thickness_dir.name}/")
                        for f in files:
                            print(f"      - {f.name}")


if __name__ == '__main__':
    main()
