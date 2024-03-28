import json
import ssl
import xmlrpc.client

# connecting to the database


with open('config.json') as json_file:
    data = json.load(json_file)
new_jvs_location = data['new_jvs_location']
processed_jvs_location = data['processed_jvs_location']
url = data['url']
db = data['db']
username = data['username']
password = data['password']
sal_id = int(data['sal'])
pur_id = int(data['pur'])
adj_id = int(data['adj'])
slip_id = int(data['slip'])



# Add error handling for connection errors
try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url) ,allow_none=True, context=ssl._create_unverified_context())
    print(common.version())

    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    if uid:
        print("Authentication successful")


except Exception as e:
    print(f'Error connecting to the database: {e}')


# creates the main journal entry
def create_main_entry(date, detail, journal_id):
    try:
        je_id = models.execute_kw(db, uid, password, 'account.move', 'create',
                                  [{'date': date, 'ref': detail, 'journal_id': journal_id
                                    }])
        return je_id
    except Exception as e:
        print(f'Error creating main journal entry: {e}')


def create_journal_line(journal_id, account_id, debit, credit, tax_boolean, partner_name="", analytic_account="",
                        label="", validity=False):
    try:
        global sale_tax_id
        global purchase_tax_id
        # print("journal id: " , journal_id)

        if tax_boolean == 1:
            journal_line = models.execute_kw(db, uid, password, 'account.move.line', 'create',
                                             [{
                                                 'move_id': journal_id,
                                                 'account_id': account_id,
                                                 'debit': debit,
                                                 'credit': credit,
                                                 'name': label,
                                                 'tax_ids': [(6, 0,[sale_tax_id])],
                                                 'partner_id': partner_name,
                                                 'analytic_account_id': analytic_account

                                             }], {'context': {'check_move_validity': validity}})
            # print(journal_line)
            #updateTaxes(journal_line)
        elif tax_boolean == 2:
            journal_line = models.execute_kw(db, uid, password, 'account.move.line', 'create',
                                             [{
                                                 'move_id': journal_id,
                                                 'account_id': account_id,
                                                 'debit': debit,
                                                 'credit': credit,
                                                 'name': label,
                                                 'tax_ids': [(6, 0, [purchase_tax_id])],
                                                 'partner_id': partner_name,
                                                 'analytic_account_id': analytic_account

                                             }], {'context': {'check_move_validity': validity}})
            # print(journal_line)
            #updateTaxes(journal_line)
        else:
            models.execute_kw(db, uid, password, 'account.move.line', 'create',

                              [{
                                  'move_id': journal_id,
                                  'account_id': account_id,
                                  'debit': debit,
                                  'credit': credit,
                                  'name': label,
                                  'partner_id': partner_name,
                                  'analytic_account_id': analytic_account

                              }], {'context': {'check_move_validity': validity}})

    except Exception as e:
        print(f'Error creating journal entry line: {e}')


def updateTaxes(journal_line):
    models.execute_kw(db, uid, password, 'account.move.line', 'write', [[journal_line],
                                                                        {
                                                                            'is_retail_pro_entry': True,
                                                                        }])


# searches odoo database for partner and returns the id
def search_partner_id(partner_name):
    if partner_name:
        try:
            # search for partner in the system
            search_partner = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                               [[['name', '=', partner_name]]],
                                               {'fields': ['id'], 'limit': 5})

            # if partner is found
            if search_partner:
                # print("partner:", partner_name, " is found in the system")
                partner_dict = search_partner[0]
                found_partner = partner_dict["id"]
                return found_partner
            # if partner is not found
            else:
                return create_partner(partner_name)
        except Exception as e:
            print(f'Error searching for partner: {e}')
    else:
        return ""


# creates new partner
def create_partner(partner_name):
    try:
        new_partner = models.execute_kw(db, uid, password, 'res.partner', 'create',
                                        [{'name': partner_name}])
        return new_partner
    except Exception as e:
        print(f'Error creating new partner: {e}')


# searches odoo database for account code and returns the id
def search_account_code_id(code):
    # searching for code in system
    try:
        search_account_code = models.execute_kw(db, uid, password, 'account.account', 'search_read',
                                                [[['code', '=', code]]],
                                                {'fields': ['id'], 'limit': 5})
        # if code is found
        if search_account_code:
            # print("account code:", code, " is found in the system")
            id_dict = search_account_code[0]
            found_id = id_dict["id"]
            return found_id
        # if code is not found
        else:
            return create_account_code(code)
    except Exception as e:
        print(f'Error searching for code: {e}')


# creates new account
def create_account_code(code):
    # print("account code:", code, " is not found in the system")
    # print("Creating new code")
    try:
        new_account_code = models.execute_kw(db, uid, password, 'account.account', 'create',
                                             [{'name': 'Account Not Found', 'code': code, 'user_type_id': 5}])
        return new_account_code
    except Exception as e:
        print(f'Error creating new code: {e}')


# search for cost center in the system
def search_cost_center_id(cost_center_name):
    if cost_center_name:
        try:
            search_cost_center = models.execute_kw(db, uid, password, 'account.analytic.account', 'search_read',
                                                   [[['name', '=', cost_center_name]]],
                                                   {'fields': ['id'], 'limit': 5})

            # if cost center is found
            if search_cost_center:
                # print("cost center:", cost_center_name, " is found in the system")
                cost_center_dict = search_cost_center[0]
                found_cost_center = cost_center_dict["id"]
                return found_cost_center
            # if cost center is not found
            else:
                return create_cost_center(cost_center_name)
        except Exception as e:
            print(f'Error searching for cost center: {e}')
    else:
        return ""


# creates new cost center
def create_cost_center(cost_center_name):
    # print("cost center:", cost_center_name, " is not found in the system")
    # print("Creating new cost center")
    try:
        new_cost_center = models.execute_kw(db, uid, password, 'account.analytic.account', 'create',
                                            [{'name': cost_center_name}])
        return new_cost_center
    except Exception as e:
        print(f'Error creating new cost center: {e}')


def search_journal_id(journal_name):
    try:
        if journal_name == "SALE":
            journal_id = sal_id
            print(sal_id)
        elif journal_name == "PUR":
            journal_id = pur_id
            print(pur_id)
        elif journal_name == "ADJ":
            journal_id = adj_id
            print(adj_id)
        elif journal_name == "SLIP":
            journal_id = slip_id
            print(slip_id)

        search_journal_id = models.execute_kw(db, uid, password, 'account.journal', 'search_read',
                                              [[['id', '=', journal_id]]],
                                              {'fields': ['id'], 'limit': 5})

        # if journal id is found
        if search_journal_id:
            journal_id_dict = search_journal_id[0]
            found_journal = journal_id_dict["id"]
            return found_journal


    except Exception as e:
        print(f'Error searching for journal id: {e}')


def search_tax_id(name):
    # searching for tax in system
    try:
        search_tax_name = models.execute_kw(db, uid, password, 'account.tax', 'search_read',
                                            [[['name', '=', name]]],
                                            {'fields': ['id'], 'limit': 5})
        # if code is found
        if search_tax_name:
            print("account code:", name, " is found in the system")
            id_dict = search_tax_name[0]
            found_id = id_dict["id"]
            return found_id
    except Exception as e:
        print(f'Error searching for code: {e}')