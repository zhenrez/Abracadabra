"""Write a new canonical-source numerical artifact bundle, without source mutation."""
import argparse
import json
from pathlib import Path
from canonical_features import build_features, write_features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source', type=Path, help='Must match the frozen canonical source byte hash')
    parser.add_argument('--font-proxy', type=Path, help='Optional explicitly selected modern font; never historical tracing')
    args = parser.parse_args()
    bundle = build_features(source_path=args.source, font_proxy=args.font_proxy)
    manifest = write_features(bundle, args.output)
    print(json.dumps({'output': str(args.output.resolve()), 'shape': list(bundle['vector'].shape),
                      'source_sha256': manifest['source']['sha256'],
                      'geometry': 'STRICT_UNAVAILABLE' if args.font_proxy is None else 'EXPLICIT_MODERN_FONT_PROXY',
                      'files': sorted(manifest['files']) + ['manifest.json']}, indent=2))


if __name__ == '__main__':
    main()
