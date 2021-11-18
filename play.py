import pandas as pd
import PySimpleGUI as sg

pd.set_option('max_columns', None)
pd.set_option('max_rows', None)
pd.set_option('display.width', None)
pd.set_option('colheader_justify', 'center')

df = pd.read_csv('sample.csv', header=0, names=[
                 'Product', 'DiscountBand', 'Sold', 'M/Price', 'S/Price', 'Discounts', 'Sales'])

layout = [[sg.Text('What you print will display below:')],
          [sg.Output(size=(100, 40), key='-OUTPUT-')],
          [sg.In(key='-IN-')],
          [sg.Button('Go'), sg.Button('Clear'), sg.Button('Exit')]]

window = sg.Window('Window Title', layout)

while True:
    event, values = window.read()
    print(df)
