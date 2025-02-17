from ksp_time_tool.common.constants import QUIT_SIGNAL, DateFormat
from ksp_time_tool.common.visitors import KSPDateNameVisitor
from ksp_time_tool.test_cli.cli_handlers import CLIInputHandler


def validate_input_format_selection(opt_str):
    cleaned = opt_str.lower().strip()
    if cleaned in ['k', 'kerbin', 'kerbal']:
        return DateFormat.KERBIN
    elif cleaned in ['e', 'earth']:
        return DateFormat.EARTH
    elif cleaned in ['u', 'ut']:
        return DateFormat.UT_SECONDS
    elif cleaned in ['q', 'quit']:
        return QUIT_SIGNAL
    return None


def main():
    """
    Main function. Converts the input time into the desired output format
    and displays it in the command line for the user.
    """
    print('KSP Time Converter')
    counter = 0
    while True:
        input_format = None
        while not input_format:
            input_format = validate_input_format_selection(
                input('Input date format ([K]erbin, [E]arth, [U]T, or [Q]uit): ')
            )
            if input_format == QUIT_SIGNAL:
                break
        if input_format == QUIT_SIGNAL:
            print('Goodbye!')
            break
        counter += 1
        input_date = CLIInputHandler(input_format).get_user_input()
        default_name = f'Time {counter}'
        name = input(f'Give this date a name (default: Time {counter}): ') or default_name
        visitor = KSPDateNameVisitor(name)
        input_date.accept_visitor(visitor)
        # Print input date in all three KSP date formats.
        print('\n----------------')
        print(input_date.name + '\n')
        print(input_date.convert_to_kerbin())
        print(input_date.convert_to_earth())
        print(input_date.convert_to_seconds())
        print('----------------\n')


if __name__ == '__main__':
    main()
