from abc import ABC
import pandas as pd
import PySimpleGUI as sg


pd.set_option('max_columns', None)
pd.set_option('max_rows', None)
pd.set_option('display.width', None)
pd.set_option('colheader_justify', 'center')

users = []
df = pd.read_csv('sample.csv', header=0, names=[
                 'Product', 'DiscountBand', 'Sold', 'M/Price', 'S/Price', 'Discounts', 'Sales'])


class User(ABC):

    def __init__(self, loginID, password, type) -> None:
        self.__loginID = loginID
        self.__password = password
        self.__type = type

    @property
    def loginID(self):
        return self.__loginID

    @property
    def password(self):
        return self.__password

    @property
    def type(self):
        return self.__type

    @password.setter
    def password(self, passw):
        self.__password = passw

    @staticmethod
    def check_credentials(users: list, login: str, password: str):
        found = False
        user = None
        for i in users:
            if (i.loginID == login and i.password == password):
                found = True
                user = i

        return found, user

    def interface(self, window, columns=None, accounts=None, account_id=None):

        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == 'Print':
                window['-OUTPUT-'].update(value='')
                print(df.loc[:, columns])
                if self.type == 'su' or self.type == 'admin':
                    window['-COL-'].update(disabled=False)
            elif event == '-PUPDATE-':
                window['-ID-'].update(self.loginID)
                window['-CPASSWD-'].update(self.password)
                if values['-NPASSWD-']:
                    self.password = values['-NPASSWD-']
                    window['-CPASSWD-'].update(self.password)
                else:
                    sg.popup_quick("Error:Missing input!")
            elif event == '-COMBO-':
                window['-CNPASSWD-'].update(disabled=False)
                for i in accounts:
                    if(i.loginID == values['-COMBO-']):
                        window['-CCPASSWD-'].update(i.password)
            elif event == '-GUPDATE-':
                if values['-CNPASSWD-']:
                    for i in accounts:
                        if(i.loginID == values['-COMBO-']):
                            i.password = values['-CNPASSWD-']
                            window['-CCPASSWD-'].update(i.password)
                else:
                    sg.popup_quick("Error: Missing input!")
            elif event == 'Create':
                if values['-CRID-'] and values['-CRPASSWD-']:
                    id = values['-CRID-']
                    passwd = values['-CRPASSWD-']

                    if id not in account_id:
                        if self.type == 'su':
                            users.append(Client(id, passwd))
                            for i in users:
                                if (isinstance(i, Client) and i.loginID not in account_id):
                                    accounts.append(i)
                                    account_id.append(i.loginID)
                        elif self.type == "admin":
                            users.append(SuperUser(id, passwd))
                            for i in users:
                                if (isinstance(i, SuperUser) and i.loginID not in account_id):
                                    accounts.append(i)
                                    account_id.append(i.loginID)
                    else:
                        sg.popup_error("ID already exists")
                        window['-CNPASSWD-'].update(disabled=True)
                        window['-CCPASSWD-'].update(value='')
                        continue

                    window['-COMBO-'].update(values=account_id)
                    sg.popup_quick_message('User created!')
                    window['-CNPASSWD-'].update(disabled=True)
                    window['-CCPASSWD-'].update(value='')
                else:
                    sg.popup_quick('Error: Missing input!')
            elif event == 'Clear':
                window['-CRID-'].update('')
                window['-CRPASSWD-'].update('')
            elif event == '-COL-':
                window['-ROW-'].update(value='',
                                       disabled=False)
                window['-CVALUE-'].update('')
            elif event == '-ROW-':

                column = values['-COL-']
                row = values['-ROW-']

                value = df.at[row, column]

                window['-CVALUE-'].update(value)
                window['-NVALUE-'].update(disabled=False)
                window['-UVALUE-'].update(disabled=False)
            elif event == '-UVALUE-':
                if values['-NVALUE-']:
                    new_value = values['-NVALUE-']
                    df.at[row, column] = new_value
                    sg.popup_quick_message('Value updated successfully!')
                    window['-OUTPUT-'].update(value='')
                    print(df)

                    window['-COL-'].update(value='')
                    window['-ROW-'].update(value='')
                    window['-CVALUE-'].update('')

                else:
                    sg.popup_quick_message('Error: Missing input!')
            elif event == 'Save As':
                try:
                    filename = values['-SAVE-']
                    df.to_csv(filename)
                    sg.popup_quick('Succesfully saved!', keep_on_top=True)
                except:
                    sg.popup_quick('Error: File name missing!',
                                   keep_on_top=True)
            elif event == 'Logout':
                window.close()
                start()
        window.close()


class Guest(User):

    def __init__(self, loginID="", password="") -> None:
        super().__init__(loginID, password, type='guest')

    def login(self):
        columns = ['Product', 'S/Price']
        layout_guest = [[sg.Output(size=(80, 40), key='-OUTPUT-',)],
                        [sg.Button('Print'), sg.Button('Logout')]]

        window = sg.Window('Login', layout=layout_guest)

        User.interface(self, window, columns)


class Client(User):
    def __init__(self, loginID, password) -> None:
        super().__init__(loginID, password, type='client')

    def login(self):
        columns = ['Product', 'S/Price', 'Discounts']

        tab_account_layout = [[sg.Text('Client ID:'), sg.Text(
            key='-ID-', size=(15, 1))],
            [sg.Text('Current Password'), sg.Text(
                key='-CPASSWD-', size=(15, 1))],
            [sg.Text('New Password'), sg.In(
                key='-NPASSWD-', do_not_clear=False)],
            [sg.Button('Update', key='-PUPDATE-')]]
        layout_client = [[sg.Output(size=(80, 40), key='-OUTPUT-',)],
                         [sg.Button('Print'), sg.Button('Logout')]]

        tab_group = [[sg.TabGroup([[sg.Tab('Main', layout_client), sg.Tab(
            'Account Management', tab_account_layout)]], tab_location='lefttop', selected_title_color='blue', border_width=5)]]

        window = sg.Window('Login', layout=tab_group)

        User.interface(self, window, columns)


class Admin(User):
    def __init__(self, loginID, password) -> None:
        super().__init__(loginID, password, type='admin')

    def login(self):

        columns = df.columns.tolist()
        rows = list(df.index.values)

        su_accounts = []
        su_id = []

        for i in users:
            if (isinstance(i, SuperUser)):
                su_accounts.append(i)
                su_id.append(i.loginID)

        frame_edit = [[sg.Text('Column', justification='center')],
                      [sg.Combo(values=columns, enable_events=True,
                                default_value='None', key='-COL-', disabled=True, tooltip='Print first to enable')],
                      [sg.Text('Row', justification='center')],
                      [sg.Combo(values=rows, enable_events=True, disabled=True,
                                key='-ROW-')],
                      [sg.Text('Current Value:', size=(15, 1)),
                       sg.Text(key='-CVALUE-',)],
                      [sg.Text('New Value:', size=(15, 1)), sg.Input(
                          disabled=True, key='-NVALUE-',
                          disabled_readonly_background_color='grey', do_not_clear=False)],
                      [sg.Button('Update', key='-UVALUE-', disabled=True)]]

        frame_save = [[sg.InputText(key='Save As', do_not_clear=False,
                                    enable_events=True, visible=False),
                       sg.FileSaveAs(file_types=(('CSV(Comma delimited) files', '*.csv'), ), initial_folder='/tmp', key='-SAVE-')]]

        frame_account_layout = [[sg.Text('Personal Details')],
                                [sg.Text('Admin ID:', size=(15, 1)), sg.Text(
                                    key='-ID-')],
                                [sg.Text('Current Password', size=(15, 1)), sg.Text(
                                    key='-CPASSWD-')],
                                [sg.Text('New Password', size=(15, 1)), sg.In(
                                    key='-NPASSWD-', do_not_clear=False)],
                                [sg.Button('Update', key='-PUPDATE-')]]

        frame_create_layout = [[sg.Text('Login ID', size=(15, 1)), sg.In(key='-CRID-', do_not_clear=False)],
                               [sg.Text('Password', size=(15, 1)), sg.In(
                                   key='-CRPASSWD-', do_not_clear=False)],
                               [sg.Button('Create'), sg.Button('Clear')]]

        frame_update_layout = [[sg.Text('SuperUser Accounts')],
                               [sg.Combo(values=su_id, default_value='None',
                                         enable_events=True, key='-COMBO-')],
                               [sg.Text('Current Password', size=(15, 1)), sg.Text(
                                   key='-CCPASSWD-')],
                               [sg.Text('New Password', size=(15, 1)), sg.In(
                                   key='-CNPASSWD-', do_not_clear=False, disabled=True, disabled_readonly_background_color='grey',)],
                               [sg.Button('Update', key='-GUPDATE-')]]

        tab_account_layout = [[sg.Frame(title='Edit Current User', layout=frame_account_layout)],
                              [sg.Frame(title='Create Super User',
                                        layout=frame_create_layout)],
                              [sg.Frame(title='Edit Super User', layout=frame_update_layout)]]

        file_layout = [[sg.Frame(title='Edit CSV', layout=frame_edit)],
                       [sg.Frame(title='Save CSV', layout=frame_save)]]

        layout_admin = [[sg.Output(size=(80, 40), key='-OUTPUT-',)],
                        [sg.Button('Print'), sg.Button('Logout')]]

        main_layout = [[sg.Column(layout_admin), sg.Column(file_layout)]]

        tab_group = [[sg.TabGroup([[sg.Tab('Main', main_layout), sg.Tab(
            'Account Management', tab_account_layout)]], tab_location='lefttop', selected_title_color='blue', border_width=5)]]

        window = sg.Window('Login', layout=tab_group)

        User.interface(self, window, columns, su_accounts, su_id)


class SuperUser(User):
    def __init__(self, loginID, password) -> None:
        super().__init__(loginID, password, type='su')

    def login(self):

        columns = df.columns.tolist()
        rows = list(df.index.values)

        client_accounts = []
        client_id = []

        for i in users:
            if (isinstance(i, Client)):
                client_accounts.append(i)
                client_id.append(i.loginID)

        frame_edit = [[sg.Text('Column', justification='center')],
                      [sg.Combo(values=columns, enable_events=True,
                                default_value='None', key='-COL-', disabled=True, tooltip='Print first to enable')],
                      [sg.Text('Row', justification='center')],
                      [sg.Combo(values=rows, enable_events=True, disabled=True,
                                key='-ROW-')],
                      [sg.Text('Current Value:', size=(15, 1)),
                       sg.Text(key='-CVALUE-',)],
                      [sg.Text('New Value:', size=(15, 1)), sg.Input(
                          disabled=True, key='-NVALUE-',
                          disabled_readonly_background_color='grey', do_not_clear=False)],
                      [sg.Button('Update', key='-UVALUE-', disabled=True)]]

        frame_save = [[sg.InputText(key='Save As', do_not_clear=False,
                                    enable_events=True, visible=False),
                       sg.FileSaveAs(file_types=(('CSV(Comma delimited) files', '*.csv'), ), initial_folder='/tmp', key='-SAVE-')]]

        frame_account_layout = [[sg.Text('Personal Details')],
                                [sg.Text('Super User ID:', size=(15, 1)), sg.Text(
                                    key='-ID-')],
                                [sg.Text('Current Password', size=(15, 1)), sg.Text(
                                    key='-CPASSWD-')],
                                [sg.Text('New Password', size=(15, 1)), sg.In(
                                    key='-NPASSWD-', do_not_clear=False)],
                                [sg.Button('Update')]]

        frame_create_layout = [[sg.Text('Login ID', size=(15, 1)), sg.In(key='-CRID-', do_not_clear=False)],
                               [sg.Text('Password', size=(15, 1)), sg.In(
                                   key='-CRPASSWD-', do_not_clear=False)],
                               [sg.Button('Create'), sg.Button('Clear')]]

        frame_update_layout = [[sg.Text('Client Accounts')],
                               [sg.Combo(values=client_id, default_value='None',
                                         enable_events=True, key='-COMBO-')],
                               [sg.Text('Current Password', size=(15, 1)), sg.Text(
                                   key='-CCPASSWD-')],
                               [sg.Text('New Password', size=(15, 1)), sg.In(
                                   key='-CNPASSWD-', do_not_clear=False, disabled=True, disabled_readonly_background_color='grey',)],
                               [sg.Button('Update', key='-GUPDATE-')]]

        tab_account_layout = [[sg.Frame(title='Edit Current User', layout=frame_account_layout)],
                              [sg.Frame(title='Create Client',
                                        layout=frame_create_layout)],
                              [sg.Frame(title='Edit Client', layout=frame_update_layout)]]

        file_layout = [[sg.Frame(title='Edit CSV', layout=frame_edit)],
                       [sg.Frame(title='Save CSV', layout=frame_save)]]

        layout_su = [[sg.Output(size=(80, 40), key='-OUTPUT-',)],
                     [sg.Button('Print'), sg.Button('Logout')]]

        main_layout = [[sg.Column(layout_su), sg.Column(file_layout)]]

        tab_group = [[sg.TabGroup([[sg.Tab('Main', main_layout), sg.Tab(
            'Account Management', tab_account_layout)]], tab_location='lefttop', selected_title_color='blue', border_width=5)]]

        window = sg.Window('Login', layout=tab_group)
        User.interface(self, window, columns, client_accounts, client_id)


def start():
    login_layout = [[sg.Text('Enter Login ID', size=(20, 1)), sg.In(key='-ID-', do_not_clear=False)],
                    [sg.Text('Enter Password', size=(20, 1)), sg.In(
                        password_char='*', key='-PASS-', do_not_clear=False)],
                    [sg.Button('Login'), sg.Button('Quit')]]

    window = sg.Window('Login', layout=login_layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Quit'):
            break

        if event == 'Login':
            success, user = User.check_credentials(
                users, values['-ID-'], values['-PASS-'])

        if success:
            window.close()
            sg.popup_quick('Successful login', title='Success',
                           auto_close_duration=0.7, keep_on_top=True)
            user.login()
        else:
            sg.popup_error("Invalid credentials", keep_on_top=True)

    window.close()


if __name__ == '__main__':

    users.append(Guest())
    users.append(Client('CL01', 'client'))
    users.append(Admin('ADM01', 'admin'))
    users.append(SuperUser('SU01', 'super'))

    start()
    exit(0)
