# coding:utf-8
import winsound
import PySimpleGUI as sg
import time
import pandas as pd

class class_timeclass:
    speech_time = 0
    remark_text = ""
    symbol = ""
    alert_over_flg = False
    alert_before_flg = False


def f_time_as_int(arg):
    if arg == None:
        return int(round(time.time() * 100))
    else:
        return int(round(time.mktime(arg.timetuple()) * 100))


# -------------------------------------------------------------------------------
# Name:                 Main処理
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    # 画面レイアウト作成
    sg.theme('Reddit')
    layout1 = [
        [sg.Text('--:--', font=('Noto Serif CJK JP',10), key='starttime'), sg.Text(' ～ ', font=('Noto Serif CJK JP',10)), sg.Text('--:--', font=('Noto Serif CJK JP',10), key='endtime')],
        [sg.Text('発表：', font=('Noto Serif CJK JP',25), key='-'), sg.Text('-', font=('Noto Serif CJK JP',25), key='presenter')],
        [sg.Text('質問：', font=('Noto Serif CJK JP',25), key='-'), sg.Text('-', font=('Noto Serif CJK JP',25), key='interrogator')],
        [sg.Text('00:00', size=(10,1), font=('Bauhaus 93',80), justification='c', key='speech_time')],
        [sg.Text('', size=(28,1), font=('Noto Serif CJK JP',30), justification='c', text_color="red", key='remark_text')],
        [sg.Button('Back', button_color=('white', 'Blue'), key='-Back-'),
        sg.Text(" "), sg.Text('-', font=('Helvetica',20), key='speach_cnt'), sg.Text(" "),
        sg.Button('Next', button_color=('white', 'Green'), key='-Next-'),
        sg.Text("      "), sg.Text('', font=('Bauhaus 93',30), key='present_time')],
    ]

    layout2 = [
        [sg.Text('*OPTIONAL*\nInput the timetable file:',size=(15,3) , justification='c'), sg.InputText(key="-filename-", readonly=True), sg.FileBrowse(key="-browsebutton-", target="-filename-", file_types=(("Excel Files", "*.xlsx"),))],
        [sg.Text('', size=(28,1), font=('Helvetica',30), justification='c', text_color="red" ,key='setting_text')],
        [sg.Text('*OPTIONAL*\n事前通知(sec):',size=(15,3) , justification='c'), sg.Combo([i for i in range(0,60*10)] + [''], default_value='0',size=(5,7), font=('Helvetica', 10), key='notify_sec')],
        [sg.Exit(button_color=('white', 'Darkred'), key='-QUIT-', pad=((0,0),(20,0)))]
    ]
    layout = [[sg.TabGroup([[sg.Tab('Timer', layout1), sg.Tab('Settings', layout2)]])]]
    window = sg.Window('Running Timer', layout, no_titlebar=True, auto_size_buttons=False, keep_on_top=True, grab_anywhere=True, element_padding=(0, 0))

    # 変数初期化
    speach_cnt = -1
    filename = None
    speechlist = []
    timeclass = class_timeclass()

    # 画面描画・各種処理
    while True:
        event, values = window.read(timeout=10)
        # ボタンクリックイベント
        if event in (sg.WIN_CLOSED, '-QUIT-'):
            break
        if event in ('-RESET-', '-SAVE-'):
            timeclass = class_timeclass()
        if event in ('-Back-') and len(speechlist):
            if speach_cnt > 0:
                speach_cnt -= 1
                timeclass = class_timeclass()
                speech_start_time = int(round(time.time() * 100))
                notify_sec = values['notify_sec']
        if event in ('-Next-') and len(speechlist):
            if speach_cnt < len(speechlist)-1:
                speach_cnt += 1
                timeclass = class_timeclass()
                speech_start_time = int(round(time.time() * 100))
                notify_sec = values['notify_sec']

        # ファイル新規読込
        if values['-filename-'] and filename != values['-filename-']:
            filename = values['-filename-']
            try:
                df = pd.read_excel(filename, sheet_name="タイムテーブル", usecols=['発表','質問','開始時刻','終了時刻'])
                for row in df.itertuples():
                    speechlist.append({"発表":row.発表, "質問":row.質問, "開始時刻":row.開始時刻, "終了時刻":row.終了時刻})
                setting_text = ""
            except Exception as e:
                setting_text = "Excelフォーマットエラー"
                timeclass = class_timeclass()
                window['-filename-'].update("")
            window['setting_text'].update(setting_text)

        # 該当行の情報取得
        if len(speechlist):
            if speach_cnt != -1:
                presenter = speechlist[speach_cnt]["発表"]
                interrogator = speechlist[speach_cnt]["質問"]
                starttime = speechlist[speach_cnt]["開始時刻"]
                endtime = speechlist[speach_cnt]["終了時刻"]

                endtime_unix = f_time_as_int(endtime)
                nowtime_unix = f_time_as_int(None)
                present_time = nowtime_unix - speech_start_time
                if endtime_unix < nowtime_unix:
                    timeclass.speech_time = nowtime_unix - endtime_unix
                    timeclass.symbol = "-"
                    timeclass.remark_text = "予定時間超過"
                    if timeclass.alert_over_flg == False and (nowtime_unix - endtime_unix <= 10 * 100): # 既に10秒以上経過しているものは初回であってもアラーム鳴らさない
                        timeclass.alert_over_flg = True
                        winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    timeclass.speech_time = endtime_unix - nowtime_unix
                    if timeclass.alert_before_flg == False and notify_sec != 0:
                        if timeclass.speech_time <= notify_sec * 100:
                            winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                            timeclass.remark_text = "残り僅か"
                            timeclass.alert_before_flg = True

                window['presenter'].update(presenter)
                window['interrogator'].update(interrogator)
                window['starttime'].update(starttime)
                window['endtime'].update(endtime)
                window['speach_cnt'].update(speach_cnt+1)
                window['speech_time'].update('{}{:02d}:{:02d}'.format(timeclass.symbol,(timeclass.speech_time // 100) // 60, (timeclass.speech_time // 100) % 60))
                window['present_time'].update('{:02d}:{:02d}'.format((present_time // 100) // 60, (present_time // 100) % 60))
                window['remark_text'].update(timeclass.remark_text)

    window.close()