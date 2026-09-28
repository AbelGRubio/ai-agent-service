from pathlib import Path

from pygenai.files.local import LocalFileSystemUnitOfWork


def test_local_basic_operations(tmp_path):
    base = tmp_path / "base"
    uow = LocalFileSystemUnitOfWork(str(base))

    # create text file
    assert uow.create_text_file("hello", "a.txt")
    assert (base / "a.txt").exists()

    # read file
    assert uow.get_file("a.txt") == b"hello"

    # list folder
    entries = uow.list_folder("")
    assert "a.txt" in entries

    # upload a local file
    src = tmp_path / "src.bin"
    src.write_bytes(b"binary")
    assert uow.upload_file(str(src), name="copied.bin")
    assert (base / "copied.bin").exists()
    assert uow.get_file("copied.bin") == b"binary"

    # move/rename
    assert uow.move_file("a.txt", "b.txt")
    assert not (base / "a.txt").exists()
    assert (base / "b.txt").exists()
    assert uow.get_file("b.txt") == b"hello"

    # delete
    assert uow.delete_file("b.txt")
    assert not (base / "b.txt").exists()

    # move route
    new_route = tmp_path / "other"
    new_route_str = uow.move_route(str(new_route))
    assert Path(new_route_str).exists()


# ensure delete on non-existing file returns False
def test_delete_nonexistent(tmp_path):
    uow = LocalFileSystemUnitOfWork(str(tmp_path / "base2"))
    assert not uow.delete_file("nope.txt")
