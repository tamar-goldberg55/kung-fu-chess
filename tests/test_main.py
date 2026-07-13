import io

from main import main


def test_main_writes_canonical_form_to_output_stream():
    input_stream = io.StringIO("wK . . .\n. wR . .\n. . bN .\n. . . bK\n")
    output_stream = io.StringIO()

    main(input_stream=input_stream, output_stream=output_stream)

    assert output_stream.getvalue() == "wK . . .\n. wR . .\n. . bN .\n. . . bK\n"


def test_main_reads_from_injected_stream_only():
    input_stream = io.StringIO(". .\n. .\n")
    output_stream = io.StringIO()

    main(input_stream=input_stream, output_stream=output_stream)

    assert output_stream.getvalue() == ". .\n. .\n"
