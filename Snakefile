from pathlib import Path

DATA_ROOT = "./data"
PDB_DIR = f"{DATA_ROOT}/pdb"
CIF_DIR = f"{DATA_ROOT}/cif"
METADATA_DIR = f"{DATA_ROOT}/metadata"
INDEX_DIR = f"{DATA_ROOT}/index"

CLI = "3dbeacons-cli"


def init():
    Path(PDB_DIR).mkdir(parents=True, exist_ok=True)
    Path(CIF_DIR).mkdir(parents=True, exist_ok=True)
    Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)


def gather_model_ids():
    init()
    pdb_dir = Path(PDB_DIR)
    cif_dir = Path(CIF_DIR)
    print(f"Searching for models in {cif_dir} ...")
    model_ids = [f.stem for f in cif_dir.iterdir() if f.suffix == '.cif']
    if not model_ids:
        print(f"Searching for models in {pdb_dir} ...")
        model_ids = [f.stem for f in pdb_dir.iterdir() if f.suffix == '.pdb']
    print(f"  ... found {len(model_ids)} model ids")
    return model_ids


model_ids = gather_model_ids()

rule all:
    input:
        expand(f"{INDEX_DIR}/{{model}}.json.loaded", model=model_ids)

rule pdb2cif:
    input:
        f"{PDB_DIR}/{{model}}.pdb"
    output:
        f"{CIF_DIR}/{{model}}.cif"
    shell:
        f"{CLI} convert-pdb2cif -i {{input}} -o {{output}}"

rule cif2index:
    input:
        f"{CIF_DIR}/{{model}}.cif", f"{METADATA_DIR}/{{model}}.json"
    output:
        f"{INDEX_DIR}/{{model}}.json"
    shell:
        f"{CLI} convert-cif2index -ic {{input[0]}} -im {{input[1]}} -o {{output}}"

rule loadindex:
    input:
        f"{INDEX_DIR}/{{model}}.json"
    output:
        f"{INDEX_DIR}/{{model}}.json.loaded"
    shell:
        f"{CLI} load-index -i {{input}} && touch {{output}}"
