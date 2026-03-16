import argparse
import sys
import json
from .sorter import AnchorLangSorter

def main():
    parser = argparse.ArgumentParser(description="Smart sorter for Minecraft lang files.")
    parser.add_argument("input", help="Path to the input lang JSON file")
    parser.add_argument("output", help="Path to the output sorted lang JSON file")
    
    args = parser.parse_args()
    
    print(f"Reading language file: {args.input}")
    try:
        with open(args.input, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{args.input}'.\nDetails: {e}")
        sys.exit(1)

    print("Clustering and sorting keys...")
    sorter = AnchorLangSorter(data)
    
    try:
        final_json_string = sorter.sort_to_json_string()
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        sys.exit(1)

    print(f"Writing sorted JSON to: {args.output}")
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(final_json_string)
        print("Done! The language file has been successfully clustered and sorted.")
    except Exception as e:
        print(f"Error: Could not write to '{args.output}'.\nDetails: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()