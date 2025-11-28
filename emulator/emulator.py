"""
CodinGame Emulator - Extensible game emulator with plugin support.

Usage:
    python emulator.py --list-models              # List available game models
    python emulator.py --model mars_lander --list # List test cases for a model
    python emulator.py --test python sol.py cave_correct  # Run a test
"""
import argparse
import sys

import models
import runner


def main():
    parser = argparse.ArgumentParser(description='CodinGame Emulator')
    parser.add_argument('--model', '-m', default='mars_lander',
                        help='Game model to use (default: mars_lander)')
    parser.add_argument('--test', type=str, nargs='+',
                        help='Test a program: --test <program> [args...] <test_case>')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--list', action='store_true',
                        help='List available test cases for selected model')
    parser.add_argument('--list-models', action='store_true',
                        help='List available game models')
    parser.add_argument('--timeout', '-t', type=int, default=150,
                        help='Timeout per turn in milliseconds (default: 150)')
    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        for name, desc in models.list_models().items():
            print(f"  {name}: {desc}")
        return

    try:
        model = models.get_model(args.model)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print(f"Test cases for {model.name}:")
        for name, desc in model.get_test_cases().items():
            print(f"  {name}: {desc}")
        return

    if args.test:
        if len(args.test) < 2:
            print("Usage: --test <program> [args...] <test_case>")
            print("       --list  to see available test cases")
            sys.exit(1)

        test_name = args.test[-1]
        program_cmd = args.test[:-1]

        if len(program_cmd) == 1 and ' ' in program_cmd[0]:
            program_cmd = program_cmd[0].split()

        # Get test case name for display
        test_cases = model.get_test_cases()
        display_name = test_cases.get(test_name, test_name)

        print(f"Model: {model.name}")
        print(f"Program: {' '.join(program_cmd)}")
        print(f"Test: {test_name} ({display_name})")
        print()

        try:
            result, trajectory, turns = runner.run_program(
                model, program_cmd, test_name, verbose=args.verbose,
                turn_timeout_ms=args.timeout
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'='*50}")
        print(f"Result: {result}")
        print(f"Turns: {turns}")

        if trajectory:
            final = trajectory[-1]
            print(f"Final: {model.format_result(final)}")

        if result == 'success':
            print("\n[OK] SUCCESS!")
            sys.exit(0)
        else:
            print("\n[FAIL] FAILED")
            print("\nLast 5 states:")
            for i, s in enumerate(trajectory[-5:]):
                print(f"  {len(trajectory)-5+i}: {model.format_result(s)}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
