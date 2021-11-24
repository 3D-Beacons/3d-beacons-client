from pathlib import Path

from .testutils import compare_files

from bio3dbeacons.cli.ciftojson import ciftojson

DATA_ROOT = Path(__file__).parent / 'gh025'


def test_example(make_example):

    file_stem = 'AF-P38398-F1-model_v1'

    example = make_example(src_root=DATA_ROOT, stems=[file_stem], copy_files=False)

    example.copy_files(types=['cif', 'metadata'])

    index_src_path = example.get_src_path('index', file_stem)
    index_tmp_path = example.get_tmp_path('index', file_stem)

    assert not index_tmp_path.exists()

    ciftojson.run(
        cif_path=str(example.get_tmp_path('cif', file_stem)),
        metadata_json_path=str(example.get_tmp_path('metadata', file_stem)),
        output_index_json_path=str(index_tmp_path))

    compare_files(got=index_tmp_path, expected=index_src_path)
