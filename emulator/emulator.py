"""
CodinGame Emulator - Extensible game emulator with plugin support.

Usage:
    python emulator.py --list-models              # List available game models
    python emulator.py --model mars_lander --list # List test cases for a model
    python emulator.py --test python sol.py cave_correct  # Run a test
    python emulator.py --model the_fall --replay test_02  # Replay trace
    python emulator.py --model the_fall --test-traces     # Test all traces for model
    python emulator.py --test-all-traces                  # Test all traces for all models
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
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Show stderr from the program (for debugging)')
    parser.add_argument('--replay', type=str, metavar='TEST_NAME',
                        help='Replay trace file and compare with CG')
    parser.add_argument('--test-traces', action='store_true',
                        help='Test all traces for selected model')
    parser.add_argument('--test-all-traces', action='store_true',
                        help='Test all traces for all models')
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
                turn_timeout_ms=args.timeout, debug=args.debug
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

    elif args.test_all_traces:
        # Test all traces for all models
        total_passed = 0
        total_failed = 0

        for model_name, desc in models.list_models().items():
            model = models.get_model(model_name)
            traces = model.list_traces()

            print(f"\n=== {model_name} ({desc}) ===")

            if not traces:
                print("  (no traces)")
                continue

            passed = 0
            failed = 0
            for trace_name in traces:
                trace = model.load_trace(trace_name)
                if not trace:
                    continue

                # Use multi-agent replay if trace has "commands" field (multi-agent format)
                if trace.get("cg_trace") and trace["cg_trace"] and "commands" in trace["cg_trace"][0]:
                    mismatches, _, _ = runner.run_replay_multi(model, trace_name, trace, verbose=args.verbose)
                else:
                    mismatches, _, _ = runner.run_replay(model, trace_name, trace, verbose=args.verbose)

                if mismatches:
                    print(f"  {trace_name}: MISMATCH at turn {mismatches[0][0]}")
                    failed += 1
                else:
                    print(f"  {trace_name}: OK")
                    passed += 1

            print(f"Results: {passed}/{passed + failed} passed")
            total_passed += passed
            total_failed += failed

        print(f"\n{'='*50}")
        print(f"TOTAL: {total_passed}/{total_passed + total_failed} passed")
        sys.exit(0 if total_failed == 0 else 1)

    elif args.test_traces:
        # Test all traces for selected model
        traces = model.list_traces()

        print(f"Testing traces for {model.name}:")

        if not traces:
            print("  (no traces)")
            sys.exit(0)

        passed = 0
        failed = 0
        for trace_name in traces:
            trace = model.load_trace(trace_name)
            if not trace:
                continue

            # Use multi-agent replay if trace has "commands" field (multi-agent format)
            if trace.get("cg_trace") and trace["cg_trace"] and "commands" in trace["cg_trace"][0]:
                mismatches, _, _ = runner.run_replay_multi(model, trace_name, trace, verbose=args.verbose)
            else:
                mismatches, _, _ = runner.run_replay(model, trace_name, trace, verbose=args.verbose)

            if mismatches:
                print(f"  {trace_name}: MISMATCH at turn {mismatches[0][0]}")
                if args.verbose:
                    for turn, diffs in mismatches:
                        for diff in diffs:
                            print(f"    T{turn}: {diff}")
                failed += 1
            else:
                print(f"  {trace_name}: OK")
                passed += 1

        print(f"\nResults: {passed}/{passed + failed} passed")
        sys.exit(0 if failed == 0 else 1)

    elif args.replay:
        # Replay a single trace
        trace_name = args.replay
        trace = model.load_trace(trace_name)

        if not trace:
            print(f"Error: Trace '{trace_name}' not found for model {model.name}", file=sys.stderr)
            sys.exit(1)

        print(f"Model: {model.name}")
        print(f"Trace: {trace_name}")
        print()

        # Use multi-agent replay if trace has "commands" field (multi-agent format)
        if trace.get("cg_trace") and trace["cg_trace"] and "commands" in trace["cg_trace"][0]:
            mismatches, trajectory, turns = runner.run_replay_multi(model, trace_name, trace, verbose=args.verbose)
        else:
            mismatches, trajectory, turns = runner.run_replay(model, trace_name, trace, verbose=args.verbose)

        print(f"\n{'='*50}")
        if mismatches:
            print(f"Result: MISMATCH")
            print(f"First mismatch at turn {mismatches[0][0]}:")
            for diff in mismatches[0][1]:
                print(f"  {diff}")
            sys.exit(1)
        else:
            print(f"Result: OK - all {turns} states match")
            sys.exit(0)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
