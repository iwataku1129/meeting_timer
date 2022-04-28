# coding:utf-8
import winsound
import PySimpleGUI as sg
import time


class class_timeclass:
    start_time, now_time = 0, 0
    first_flag = True
    second_flag = False
    paused_flg = True
    alert1_flg = False
    alert2_flg = False
    remark_text = ""
    symbol = ""


def f_time_as_int():
    return int(round(time.time() * 100))


# -------------------------------------------------------------------------------
# Name:                 Main処理
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    # 画面レイアウト作成
    sg.theme('Reddit')
    layout1 = [
        [sg.Text('', size=(10,1), font=('Bauhaus 93',80), justification='c', pad=((30,30),(20,0)), key='speech_time')],
        [sg.Text('', size=(28,1), font=('Helvetica',30), justification='c', pad=((0,0),(0,10)) ,key='speech_text')],
        [sg.Text('', size=(28,1), font=('Helvetica',30), justification='c', pad=((0,0),(0,10)), text_color="red" ,key='remark_text')],
        [sg.Button('Run', button_color=('white', 'Blue'), key='-RUN-PAUSE-'),
        sg.Button('Reset', button_color=('white', 'Green'), key='-RESET-')]
    ]

    layout2 = [
        [sg.Text('*OPTIONAL*\nInput the time title:',size=(15,2), justification='c', pad=((0,0),(10,10))), sg.InputText(default_text='presentation time' ,key='speech_title')],
        [sg.Combo([i for i in range(0,60)] + [''], default_value='10',size=(5,7) , font=('Helvetica', 10), pad=((125,0),(0,0)), key='speech_min'),
        sg.Text('min.', font=('Helvetica', 10)),
        sg.Combo([i for i in range(0,60)] + [''], default_value='0',size=(5,7), font=('Helvetica', 10), key='speech_sec'),
        sg.Text('sec.    事前通知:', font=('Helvetica', 10)),
        sg.Combo([i for i in range(0,60*10)] + [''], default_value='60',size=(5,7), font=('Helvetica', 10), key='speech_notify_sec'),
        sg.Text('sec.(残り時間)', font=('Helvetica', 10))],
        [sg.Text('')],
        [sg.Text('*OPTIONAL*\nInput the additionnal time title:',size=(15,3) , justification='c', pad=((0,0),(0,0))), sg.InputText(default_text='Q&A' ,key='add_title')],
        [sg.Combo([i for i in range(0,60)] + [''], default_value='0',size=(5,5) , font=('Helvetica', 10), pad=((125,0),(0,0)), key='add_min'),
        sg.Text('min.', font=('Helvetica', 10)),
        sg.Combo([i for i in range(0,60)] + [''], default_value='0',size=(5,5), font=('Helvetica', 10), key='add_sec'),
        sg.Text('sec.    事前通知:', font=('Helvetica', 10)),
        sg.Combo([i for i in range(0,60*10)] + [''], default_value='0',size=(5,7), font=('Helvetica', 10), key='add_notify_sec'),
        sg.Text('sec.(残り時間)', font=('Helvetica', 10))],
        [sg.Button('SAVE', button_color=('white', 'Green'), key='-SAVE-', pad=((0,0),(20,0))),
        sg.Exit(button_color=('white', 'Darkred'), key='-QUIT-', pad=((0,0),(20,0)))]
    ]
    layout = [[sg.TabGroup([[sg.Tab('Timer', layout1), sg.Tab('Settings', layout2)]])]]
    window = sg.Window('Running Timer', layout, no_titlebar=True, auto_size_buttons=False, keep_on_top=True, grab_anywhere=True, element_padding=(0, 0))

    # 変数初期化
    timeclass = class_timeclass()

    # 画面描画・各種処理
    while True:
        event, values = window.read(timeout=10)
        # ボタンクリックイベント
        if event in (sg.WIN_CLOSED, '-QUIT-'):
            break
        if event in ('-RESET-', '-SAVE-'):
            timeclass = class_timeclass()
        elif event == '-RUN-PAUSE-':
            timeclass.paused_flg = not timeclass.paused_flg
            if not timeclass.first_flag and not timeclass.paused_flg:
                if not timeclass.alert2_flg:
                    speech_time = timeclass.now_time
                else:
                    speech_time = -timeclass.now_time
            timeclass.start_time = f_time_as_int()
            window['-RUN-PAUSE-'].update('Run' if timeclass.paused_flg else 'Pause')

        # 計測演算
        if timeclass.first_flag:
            if not timeclass.second_flag:            
                # 初回処理 (option1)
                speech_time = values['speech_min'] * 100 * 60 + values['speech_sec'] * 100
                add_time = values['add_min'] * 100 * 60 + values['add_sec'] * 100
                speech_notify_sec = values['speech_notify_sec'] * 100
                add_notify_sec = values['add_notify_sec'] * 100
                remark_word = values['speech_title']
                timeclass.now_time = speech_time
            else:
                # 初回処理 (option2)
                timeclass.start_time = f_time_as_int()
                speech_time = add_time + 100
                speech_notify_sec = add_notify_sec
                remark_word = values['add_title']
                timeclass.now_time = speech_time
            timeclass.first_flag = False
        elif timeclass.paused_flg:
            # paused処理
            pass
        else:
            # 計測時
            timeclass.now_time = speech_time - (f_time_as_int() - timeclass.start_time)
            if timeclass.now_time <= 0 and not timeclass.alert2_flg:
                winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                timeclass.remark_text = "!!時間超過!!"
                timeclass.alert2_flg = True
            elif speech_notify_sec != 0 and timeclass.now_time <= speech_notify_sec and not timeclass.alert1_flg:
                winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                timeclass.remark_text = "残り僅か"
                timeclass.alert1_flg = True

            if timeclass.alert2_flg:
                if timeclass.second_flag == False and add_time != 0:
                    timeclass = class_timeclass()
                    timeclass.paused_flg = False
                    timeclass.second_flag = True
                else:
                    timeclass.now_time = 100 + (f_time_as_int() - timeclass.start_time - speech_time) # マイナス表示
                    timeclass.symbol = "-"

        window['speech_time'].update('{}{:02d}:{:02d}'.format(timeclass.symbol,(timeclass.now_time // 100) // 60, (timeclass.now_time // 100) % 60))
        window['speech_text'].update(remark_word)
        window['remark_text'].update(timeclass.remark_text)

    window.close()