#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

INCOME_CMD = "income"
COST_CMD = "cost"
STATS_CMD = "stats"

EXIT_CMD = "exit"

Date = tuple[int, int, int]

MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MIN_YEAR = 1

FEBRUARY = 2
DAYS_IN_LEAP_FEBRUARY = 29

DATE_LENGTH = 10
FIRST_SEPARATOR_INDEX = 2
SECOND_SEPARATOR_INDEX = 5
DATE_SEPARATOR = "-"

DAY_SLICE_END = 2
MONTH_SLICE_START = 3
MONTH_SLICE_END = 5
YEAR_SLICE_START = 6

CATEGORY_SEPARATOR = "::"

MONTH_DAYS_COMMON = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    '''
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    '''
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY and is_leap_year(year):
        return DAYS_IN_LEAP_FEBRUARY
    return MONTH_DAYS_COMMON[month]


def is_valid_date_parts(day: int, month: int, year: int) -> bool:
    if year < MIN_YEAR:
        return False
    if month < MIN_MONTH or month > MAX_MONTH:
        return False
    if day < MIN_DAY:
        return False
    if day > get_days_in_month(month, year):
        return False
    return True


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    '''
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    '''
    if len(maybe_dt) != DATE_LENGTH:
        return None

    if maybe_dt[FIRST_SEPARATOR_INDEX] != DATE_SEPARATOR:
        return None
    if maybe_dt[SECOND_SEPARATOR_INDEX] != DATE_SEPARATOR:
        return None

    day_part = maybe_dt[:DAY_SLICE_END]
    month_part = maybe_dt[MONTH_SLICE_START:MONTH_SLICE_END]
    year_part = maybe_dt[YEAR_SLICE_START:]

    if not day_part.isdigit():
        return None
    if not month_part.isdigit():
        return None
    if not year_part.isdigit():
        return None

    day = int(day_part)
    month = int(month_part)
    year = int(year_part)

    if not is_valid_date_parts(day, month, year):
        return None

    return day, month, year


def parse_amount(maybe_amount: str) -> float | None:
    '''
    Парсит число из строки.
    :param str maybe_amount: Проверяемая строка
    :return: Число или None, если строка не число.
    :rtype: float | None
    '''
    if maybe_amount == "":
        return None

    normalized = ""
    has_digit = False
    has_separator = False

    for index, ch in enumerate(maybe_amount):
        if ch.isdigit():
            normalized += ch
            has_digit = True
            continue

        if index == 0 and (ch == "+" or ch == "-"):
            normalized += ch
            continue

        if ch == "," or ch == ".":
            if has_separator:
                return None
            has_separator = True
            normalized += "."
            continue

        return None

    if not has_digit:
        return None

    if normalized.endswith("."):
        return None

    if normalized == "+" or normalized == "-":
        return None

    return float(normalized)


def split_category_name(category_name: str) -> tuple[str, str | None]:
    if CATEGORY_SEPARATOR not in category_name:
        return category_name, None

    if category_name.count(CATEGORY_SEPARATOR) != 1:
        return "", None

    separator_index = category_name.find(CATEGORY_SEPARATOR)
    common_category = category_name[:separator_index]
    target_category = category_name[separator_index + len(CATEGORY_SEPARATOR):]

    return common_category, target_category


def is_valid_category_name(category_name: str) -> bool:
    common_category, target_category = split_category_name(category_name)

    if common_category not in EXPENSE_CATEGORIES:
        return False

    target_categories = EXPENSE_CATEGORIES[common_category]

    if len(target_categories) == 0:
        return target_category is None

    if target_category is None:
        return False

    return target_category in target_categories


def build_available_categories() -> list[str]:
    categories: list[str] = []

    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        if len(target_categories) == 0:
            categories.append(common_category)
        else:
            for target_category in target_categories:
                categories.append(common_category + CATEGORY_SEPARATOR + target_category)

    return categories


def cost_categories_handler() -> str:
    return "\n".join(build_available_categories())


def build_category_error_message() -> str:
    categories_text = cost_categories_handler()
    return NOT_EXISTS_CATEGORY + "\n" + categories_text


def format_money(amount: float) -> str:
    return f"{amount:.2f}"


def is_same_month(left: Date, right: Date) -> bool:
    return left[1] == right[1] and left[2] == right[2]


def is_date_not_later(left: Date, right: Date) -> bool:
    if left[2] != right[2]:
        return left[2] < right[2]

    if left[1] != right[1]:
        return left[1] < right[1]

    return left[0] <= right[0]


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {
            "type": INCOME_CMD,
            "amount": amount,
            "date": income_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {
            "type": COST_CMD,
            "category": category_name,
            "amount": amount,
            "date": income_date,
        }
    )
    return OP_SUCCESS_MSG


def get_detail_name(category_name: str) -> str:
    common_category, target_category = split_category_name(category_name)

    if target_category is None:
        return common_category

    return target_category


def add_amount_by_category(
    details_map: dict[str, float],
    category_name: str,
    amount: float,
) -> None:
    if category_name not in details_map:
        details_map[category_name] = 0.0

    details_map[category_name] += amount


def collect_stats_data(report_date_parts: Date) -> dict[str, Any]:
    total_income = 0.0
    total_expenses = 0.0
    month_income = 0.0
    month_expenses = 0.0
    details_map: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        transaction_date = transaction.get("date")
        if not isinstance(transaction_date, str):
            continue

        transaction_date_parts = extract_date(transaction_date)
        if transaction_date_parts is None:
            continue

        if not is_date_not_later(transaction_date_parts, report_date_parts):
            continue

        amount = transaction.get("amount")
        if not isinstance(amount, float) and not isinstance(amount, int):
            continue

        transaction_type = transaction.get("type")

        if transaction_type == INCOME_CMD:
            total_income += amount
            if is_same_month(transaction_date_parts, report_date_parts):
                month_income += amount

        elif transaction_type == COST_CMD:
            total_expenses += amount
            if is_same_month(transaction_date_parts, report_date_parts):
                month_expenses += amount

                category_name = transaction.get("category")
                if isinstance(category_name, str):
                    add_amount_by_category(details_map, category_name, amount)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "month_income": month_income,
        "month_expenses": month_expenses,
        "details_map": details_map,
    }


def build_month_result_line(month_income: float, month_expenses: float) -> str:
    month_result = month_income - month_expenses

    if month_result >= 0:
        return (
            "This month, the profit amounted to "
            + format_money(month_result)
            + " rubles."
        )

    return (
        "This month, the loss amounted to "
        + format_money(-month_result)
        + " rubles."
    )


def build_details_lines(details_map: dict[str, float]) -> list[str]:
    lines: list[str] = []
    category_names = sorted(details_map.keys())

    index = 1
    for category_name in category_names:
        detail_name = get_detail_name(category_name)
        line = (
            str(index)
            + ". "
            + detail_name
            + ": "
            + format_money(details_map[category_name])
        )
        lines.append(line)
        index += 1

    return lines


def build_stats_lines(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    details_map: dict[str, float],
) -> list[str]:
    lines = [
        "Your statistics as of " + report_date + ":",
        "Total capital: " + format_money(total_capital) + " rubles",
        build_month_result_line(month_income, month_expenses),
        "Income: " + format_money(month_income) + " rubles",
        "Expenses: " + format_money(month_expenses) + " rubles",
        "",
        "Details (category: amount):",
    ]

    details_lines = build_details_lines(details_map)
    for line in details_lines:
        lines.append(line)

    return lines


def stats_handler(report_date: str) -> str:
    report_date_parts = extract_date(report_date)
    if report_date_parts is None:
        return INCORRECT_DATE_MSG

    stats_data = collect_stats_data(report_date_parts)

    total_capital = stats_data["total_income"] - stats_data["total_expenses"]

    lines = build_stats_lines(
        report_date,
        total_capital,
        stats_data["month_income"],
        stats_data["month_expenses"],
        stats_data["details_map"],
    )
    return "\n".join(lines)


def handle_income_command(command_args: list[str]) -> str:
    if len(command_args) != 2:
        return UNKNOWN_COMMAND_MSG

    amount_text = command_args[0]
    income_date = command_args[1]

    amount = parse_amount(amount_text)
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    return income_handler(amount, income_date)


def handle_cost_command(command_args: list[str]) -> str:
    if len(command_args) == 1 and command_args[0] == "categories":
        return cost_categories_handler()

    if len(command_args) != 3:
        return UNKNOWN_COMMAND_MSG

    category_name = command_args[0]
    amount_text = command_args[1]
    cost_date = command_args[2]

    if not is_valid_category_name(category_name):
        return build_category_error_message()

    amount = parse_amount(amount_text)
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(cost_date) is None:
        return INCORRECT_DATE_MSG

    return cost_handler(category_name, amount, cost_date)


def handle_stats_command(command_args: list[str]) -> str:
    if len(command_args) != 1:
        return UNKNOWN_COMMAND_MSG

    report_date = command_args[0]
    if extract_date(report_date) is None:
        return INCORRECT_DATE_MSG

    return stats_handler(report_date)


COMMAND_HANDLERS = {
    INCOME_CMD: handle_income_command,
    COST_CMD: handle_cost_command,
    STATS_CMD: handle_stats_command,
}


def parse_command_line(command_line: str) -> tuple[str, list[str]] | None:
    parts = command_line.split()
    if len(parts) == 0:
        return None

    return parts[0], parts[1:]


def get_command_handler(command_name: str):
    if command_name not in COMMAND_HANDLERS:
        return None

    return COMMAND_HANDLERS[command_name]


def budget_app_executor(command_line: str) -> str:
    parsed_command = parse_command_line(command_line)
    result = UNKNOWN_COMMAND_MSG

    if parsed_command is not None:
        command_name, command_args = parsed_command
        command_handler = get_command_handler(command_name)

        if command_handler is not None:
            result = command_handler(command_args)

    print(result)
    return result


def main() -> None:
    while True:
        command_line = input().strip()
        if command_line == EXIT_CMD:
            break
        budget_app_executor(command_line)


if __name__ == "__main__":
    main()
