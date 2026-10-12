"""Official judge CLI with a header-inclusive source-cache namespace.

The installed 1.1.0 C++ cache fingerprints translation units but omits headers.
Stage an immutable copy under a name derived from all project inputs before
calling its unmodified compiler. Engine, compiler and judge flags stay intact.
"""
import hashlib
import os
import pathlib
import shutil
import sys
import tempfile


def freeze(directory, cache):
    directory = pathlib.Path(directory)
    excluded = {'.git', '.unswbc-build', 'build', 'replays', '__pycache__', '.DS_Store'}
    inputs = []
    for p in sorted(directory.rglob('*')):
        rel = p.relative_to(directory)
        if any(part in excluded for part in rel.parts) or p.suffix == '.wasm':
            continue
        if p.is_symlink():
            raise ValueError('Bot project must not contain symlinks: ' + str(rel))
        if p.is_file():
            inputs.append((rel, p.read_bytes()))
    digest = hashlib.sha256()
    for rel, content in inputs:
        name = rel.as_posix().encode()
        digest.update(len(name).to_bytes(8, 'big') + name)
        digest.update(len(content).to_bytes(8, 'big') + content)
    target = pathlib.Path(cache) / ('project-' + digest.hexdigest())
    if target.is_dir():
        for rel, content in inputs:
            if (target / rel).read_bytes() != content:
                raise ValueError('Immutable compiler input cache changed')
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = pathlib.Path(tempfile.mkdtemp(prefix='.stage-', dir=target.parent))
    try:
        for rel, content in inputs:
            (temporary / rel).parent.mkdir(parents=True, exist_ok=True)
            (temporary / rel).write_bytes(content)
        try:
            temporary.rename(target)
        except OSError:
            if not target.is_dir():
                raise
            for rel, content in inputs:
                if (target / rel).read_bytes() != content:
                    raise ValueError('Concurrent compiler input cache differs')
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return target


def main():
    from unswbc import clangtool
    from unswbc.cli import main as official_main
    original = clangtool.build
    cache = pathlib.Path(os.environ['XDG_CACHE_HOME']) / 'unswbc-projects'
    clangtool.build = lambda directory: original(freeze(directory, cache))
    return official_main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
