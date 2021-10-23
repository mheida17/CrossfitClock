import datetime
import time
import wx
import pdb

if False:
    '''Toggled during debuging'''
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame


COUNTDOWN_SEC = 10


class EMOM:
    def __init__(self, wod):
        self.wod_type = "EMOM"
        self.work_time = 60
        self.rest_time = 0
        self.is_active = False
        self.round = 0
        # Read this from the workout
        for line in wod:
            if "Rounds: " in line:
                try:
                    self.iterations = int(line.split(": ")[1])
                except ValueError:
                    print(f"Could not extract number of rounds {line}")
                    exit(1)
        self.description = wod


class RFT:
    def __init__(self, wod):
        pass


class AMRAP:
    def __init__(self, wod):
        pass


class Chipper:
    def __init__(self, wod):
        pass


class Tabata:
    def __init__(self, wod):
        pass


class MyPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

    def onKey(self, event):
        """
        Handle button events in case no mouse is used
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.GetParent().Close()
        elif key_code == wx.WXK_SPACE:
            if self.GetParent().isTimerActive():
                self.GetParent().stop(event)
            else:
                self.GetParent().start(event)
        else:
            event.Skip()


class CrossfitClock(wx.Frame):
    def __init__(self, wod, strength_description):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Crossfit WOD")
        self.panel = MyPanel(self)
        self.SetBackgroundColour("black")

        # TODO: add a round panel
        panelGridSizer = wx.GridSizer(rows=2, cols=1, hgap=5, vgap=5)
        workoutGridSizer = wx.GridSizer(rows=1, cols=2, hgap=5, vgap=5)
        buttonGridSizer = wx.GridSizer(rows=1, cols=3, hgap=5, vgap=5)
        timerGridSizer = wx.GridSizer(rows=1, cols=2, hgap=5, vgap=5)
        font = wx.Font(24, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        timeFont = wx.Font(
            256, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        self.wod = wod
        self.countdown_timer = 3
        self.firstStart = True

        self.timerLabel = wx.StaticText(
            self.panel,
            wx.ID_ANY,
            label=str(datetime.timedelta(seconds=self.wod.work_time))[2:],
        )
        self.timerLabel.SetFont(timeFont)
        self.timer_sec = self.wod.work_time

        self.workoutLabel = wx.StaticText(self.panel, wx.ID_ANY, wod.description)
        self.workoutLabel.SetFont(font)

        self.strengthLabel = wx.StaticText(self.panel, wx.ID_ANY, strength_description)
        self.strengthLabel.SetFont(font)

        startBtn = wx.Button(self.panel, label="Start Countdown")
        startBtn.Bind(wx.EVT_BUTTON, self.start)
        stopBtn = wx.Button(self.panel, label="Stop Countdown")
        stopBtn.Bind(wx.EVT_BUTTON, self.stop)
        closeBtn = wx.Button(self.panel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.close)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

        workoutGridSizer.Add(self.workoutLabel, 0, wx.ALIGN_LEFT)
        workoutGridSizer.Add(self.strengthLabel, 0, wx.ALIGN_RIGHT)

        buttonGridSizer.Add(startBtn, 0, wx.EXPAND)
        buttonGridSizer.Add(stopBtn, 0, wx.EXPAND)
        buttonGridSizer.Add(closeBtn, 0, wx.EXPAND)

        timerGridSizer.Add(self.timerLabel, 0, wx.EXPAND)
        timerGridSizer.Add(
            buttonGridSizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL
        )

        panelGridSizer.Add(workoutGridSizer, 0, wx.ALIGN_CENTER)
        panelGridSizer.Add(timerGridSizer, 0, wx.ALIGN_CENTER)

        self.panel.SetSizer(panelGridSizer)

        self.ShowFullScreen(True)
        self.Show()

    def start(self, event):
        if self.firstStart is True:
            self.timer_sec = COUNTDOWN_SEC
        self.isActive = True
        self.timer.Start(1000)

    # TODO: The timing seems a bit off when transitioning from the countdown to the workout
    # TODO: This can be better separated, need to transition my white board into plantUML to then be implemented
    # TODO: should also play sounds at the end of specific workouts (ie EMOM) but not for others (ie RFT)
    def update(self, event):
        if self.firstStart is True:
            pygame.mixer.init()
            if 0 < self.timer_sec <= 3:
                pygame.mixer.music.load("short_beep.mp3")
                pygame.mixer.music.play()

            self.timerLabel.SetLabel(
                str(datetime.timedelta(seconds=self.timer_sec))[2:]
            )
            self.timer_sec -= 1
            if self.timer_sec < 0:
                self.timer_sec = self.wod.work_time + 1
                self.firstStart = False
                pygame.mixer.music.load("long_beep.mp3")
                pygame.mixer.music.play()
                self.wod.round += 1
            return

        self.timer_sec -= 1
        if self.timer_sec < 0:
            if self.wod.iterations > 1:
                self.wod.iterations -= 1
                self.wod.round += 1
                self.timer_sec = self.wod.work_time
                self.timerLabel.SetLabel(
                    str(datetime.timedelta(seconds=self.timer_sec))[2:]
                )
            else:
                self.timer.Stop()
                self.isActive = False
                pygame.mixer.init()
                pygame.mixer.music.load("long_beep.mp3")
                pygame.mixer.music.play()
            return
        else:
            self.timerLabel.SetLabel(
                str(datetime.timedelta(seconds=self.timer_sec))[2:]
            )

    def stop(self, event):
        self.isActive = False
        self.timer.Stop()

    def close(self, event):
        self.Close()

    def isTimerActive(self):
        if self.isActive:
            return True
        else:
            return False


if __name__ == "__main__":
    with open("wod_file.txt", "r") as wod_file:
        wod = wod_file.read()
    with open("strength_file.txt", "r") as strength_file:
        strength = strength_file.read()
    app = wx.App(False)

    # Determine what type of workout this is
    if "EMOM" in wod:
        todays_wod = EMOM(wod)
    elif "RFT" in wod or "Rounds for Time" in wod:
        todays_wod = RFT(wod)
    elif "AMRAP" in wod:
        todays_wod = AMRAP(wod)
    elif "Chipper" in wod:
        todays_wod = Chipper(wod)
    elif "Tabata" in wod:
        todays_wod = Tabata(wod)
    else:
        print("Unknown workout type, exiting")
        exit(1)

    frame = CrossfitClock(todays_wod, strength)
    app.MainLoop()
