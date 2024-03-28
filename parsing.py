from datetime import datetime, timedelta
import tools


class ODOOPostingType:
    def __init__(self, account_code: str, partner: str, cost_center_code: str, debit: float, credit: float, label: str,
                 tax_boolean: float):
        self.account_code = account_code
        self.partner = partner
        self.cost_center_code = cost_center_code
        self.debit = debit
        self.credit = credit
        self.label = label
        self.tax_boolean = tax_boolean


def process_file(file_path: str):
    posting_arr = []

    with open(file_path, 'r') as f:
        # Skip header text fields
        f.readline()

        # Read header data
        header_data = f.readline().strip()
        str_read_field = header_data.split('\t')
        if len(str_read_field) > 0:
            trans_code = str_read_field[0]
        if len(str_read_field) > 1:
            date_string = str_read_field[1].strip()
            print(date_string)
            date_format = "%d/%m/%Y"
            date = datetime.strptime(date_string, date_format)
            trans_date = date.strftime("%Y-%m-%d")

        if len(str_read_field) > 2:
            detail = str_read_field[2]

        # Skip details text fields
        f.readline()

        # Read details data
        for line in f:
            str_read_field = line.strip().split('\t')
            account_code = str_read_field[0] if len(str_read_field) > 0 else ""
            partner = str_read_field[1] if len(str_read_field) > 1 else ""
            cost_center_code = str_read_field[2] if len(str_read_field) > 2 else ""
            debit = float(str_read_field[3]) if len(str_read_field) > 3 else 0.0
            credit = float(str_read_field[4]) if len(str_read_field) > 4 else 0.0
            label = str_read_field[5] if len(str_read_field) > 5 else ""
            tax_boolean = float(str_read_field[6]) if len(str_read_field) > 6 else 0.0
            posting_arr.append(
                ODOOPostingType(account_code, partner, cost_center_code, debit, credit, label, tax_boolean))

    # create main journal entry

    # checking tax
    # choose journal to post method in

    main_jv = tools.create_main_entry(trans_date, detail, tools.search_journal_id(trans_code))
    # loop through each line and create the journal lines
    for i, item in enumerate(posting_arr):
        if i == len(posting_arr) - 1:
            tools.create_journal_line(main_jv, tools.search_account_code_id(item.account_code), item.debit, item.credit,
                                      item.tax_boolean,
                                      tools.search_partner_id(item.partner),
                                      tools.search_cost_center_id(item.cost_center_code), item.label)
        else:
            tools.create_journal_line(main_jv, tools.search_account_code_id(item.account_code), item.debit, item.credit,
                                      item.tax_boolean,
                                      tools.search_partner_id(item.partner),
                                      tools.search_cost_center_id(item.cost_center_code), item.label)
