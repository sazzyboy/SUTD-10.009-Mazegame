import time
from threading import Thread
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

Window.size = (600, 600)  # set size of the window to a fixed 600x600, can be modified so according to user's preference. 

class Screenmanager(ScreenManager):
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        self.add_widget(Instruction_ui())  

class Instruction_ui(Screen):  # this is class for instruction UI Window
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'instr'  # name of the screen for instruction screen, first screen
        self.instr = Label(
            text='[b]Welcome to the maze[/b]\n\n Instructions to move:\n W - Up, A - Left, S - Down, D - Right\n\n 1. Reach the end point (green marker) within 60s\n 2. If you reach it in 60s, you win\n3. If you fail to reach in 60s, you lose\n4. Press button to start! \n\nEnjoy!',
            valign="middle", halign="center", size_hint_y=.5, markup=True) # this is a text box or Label that contains the instructions to the game plus how to play it
        self.startGame = Button(text='Start Game', pos_hint={'x': .4}, size_hint_y=.05, size_hint_x=None, width=120,
                           halign='center')  # create button that brings us to the main game page
        self.startGame.bind(on_release=self.switch2Main) #callback to bring us to the main game page
        self.lbl = Label(size_hint_y=.45) # this is where the text would be, so if the window changes it follows the ratio of the window's y axis and size
        self.box = BoxLayout(orientation='vertical')  # create box layout with vertical orientation
        self.box.add_widget(self.instr)  # add widgets to boxlayout
        self.box.add_widget(self.startGame)
        self.box.add_widget(self.lbl)
        self.add_widget(self.box)  # add boxlayout to the Screen

    def switch2Main(self, t):
        self.manager.add_widget(GameWidget())
        self.manager.current = 'main'  # switch to main UI which is GameWidget Screen

class GameWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.CD = 60  # initialize counter down time on second, setting to 60 seconds first (can be adjusted accordingly)
        self.youWin = False  # variable for detection if win or lose
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)  # callback when keyboard is closed
        self._keyboard.bind(on_key_down=self._on_key_down)

        self.init_App()

    def init_App(self):

        self.layout = GridLayout(cols=35) #set up a 35x35 grid since my game uses a nested list of 35 lists with 35 elements
        self.add_widget(self.layout)

        self.label = Label(text='', color=[1, 0, 0, 1], pos=(230, 285)) #timer countdoww label to be created
        self.add_widget(self.label)

        self.widget_maze = []
        maze_file = open('maze.txt', 'r') #using a text file to make the code look cleaner
        
        for index, line in enumerate(maze_file):
            row = line.rstrip().split(' ')
            widget_row = []
            for text in row: #flips and becomes y,x since index refers to the row and col refer to the x coordinate
                if text == 'x': #from kivy documentation, we can see that the buttons takes on default values that dictate the appearance. the empty string gives a blank appearance and can take on the color that i have assigned, and when pressed or not pressed it will retain that color consistently.
                    widget_row.append(Button(background_color=[0, 0, 0, 1],disabled=True,background_disabled_normal='',background_disabled_down='')) #black color to denote the borders
                elif text == 's':
                    widget_row.append(Button(background_color=[1, 0, 0, 1],disabled=True,background_disabled_normal='',background_disabled_down='')) #red color to denote where the player is 
                    col = row.index(text)
                    self.red_pos = (index, col) 
                elif text == 'W':
                    widget_row.append(Button(background_color=[0, 1, 0, 1], disabled=True, background_disabled_normal='', background_disabled_down='')) #green color to denote end point                  
                    col = row.index(text)
                    self.win_pos = (index, col)
                else:
                    widget_row.append(Button(background_color=[1, 1, 1, 1], disabled=True, background_disabled_normal='', background_disabled_down='')) #white color to denote moveable path
            self.widget_maze.append(widget_row)
        
        maze_file.close()

        for row in self.widget_maze:
            for widget in row:
                self.layout.add_widget(widget)

        Thread(target=self.TimerCD).start()  # open the counter in new thread to avoid UI crashing or hanging, and to start when the maze game screen is switched to hence its at the end

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.movemechanism(text) #text is from the keycode tuple

    def movemechanism(self, key):  
        try:
            y = self.red_pos[0] #y coordinate of the player since i flipped it around above in index and col
            x = self.red_pos[1] #x coordinate of the player since i flipped it around above in index and col

            #checking if text == text of the key pressed 
            if "w" == key:  
                if self.widget_maze[y-1][x].background_color != [0,0,0,1]:   #if its not black, we can move up one grid and update the colors around
                    self.widget_maze[y][x].background_color = [1,1,1,1] #white to denote the previous position held by the red player
                    self.widget_maze[y-1][x].background_color = [1,0,0,1] #the new grid that holds the player, having moved one step up
                    self.red_pos = (y-1, x) #update the new position
                    if self.red_pos[0] == self.win_pos[0] and self.red_pos[1] == self.win_pos[1]: #from above, if the players position matches the winnig position, it changes the winning condition
                        self.youWin = True 
            if "s" == key:
                if self.widget_maze[y + 1][x].background_color != [0,0,0,1]: 
                    self.widget_maze[y][x].background_color = [1,1,1,1] 
                    self.widget_maze[y+1][x].background_color = [1,0,0,1] #the new grid that holds the red player, having moved one step down
                    self.red_pos = (y+1, x)
            if "a" == key:
                if self.widget_maze[y][x - 1].background_color != [0,0,0,1]: 
                    self.widget_maze[y][x].background_color = [1,1,1,1]
                    self.widget_maze[y][x-1].background_color = [1,0,0,1] #the new grid that holds the red player, having moved one step left
                    self.red_pos = (y,x-1)
            if "d" == key:
                if self.widget_maze[y][x + 1].background_color != [0,0,0,1]:
                    self.widget_maze[y][x].background_color = [1,1,1,1]
                    self.widget_maze[y][x+1].background_color = [1,0,0,1] #the new grid that holds the red player, having moved one step right
                    self.red_pos = (y, x+1)
             
        except:
            print('error') #if press other keys, it will print error to show invalid key pressed
            

    def TimerCD(self):  # this function will keep running until the count down will be zero or when you win and display the popup
        while True:
            if self.CD != 0: #while time remains on the timer
                self.label.text = ("Time Remains %d (s)" % self.CD)
                time.sleep(1) #halts the function by 1 second before updating
                self.CD -= 1 #reduce count by 1 second
                if self.youWin: #if reach end point
                    self.label.text = ("Time Remains %d (s)" % self.CD)
                    self.popup_display('Game Info', 'YOU WIN.')
                    self._on_keyboard_closed() #break keyboard input, unbind the keyboard action
                    break
            else:
                self.label.text = ("Time Remains %d (s)" % self.CD)
                self.popup_display('Game Info', 'YOU LOSE.')
                self._on_keyboard_closed() 
                break

    def popup_display(self, title, message):  # this popup function is for displaying MSG when you win or los
        btnclose = Button(text='Close', size_hint_y=None, height=30, background_normal='', color=(0, 0, 0, 1))
        lbl = Label(text=message, valign="middle", bold=True, halign="center")
        content = BoxLayout(orientation='vertical')
        content.add_widget(lbl)
        content.add_widget(btnclose)
        popup = Popup(content=content, title=title, size_hint=(None, None), size=(300, 300), auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        popup.open()

class MyApp(App):
    def build(self):
        self.title = 'MAZE GAME'
        sm = Screenmanager() #runs the build method first before it runs the instruction UI
        return sm

if __name__ == "__main__":
    MyApp().run()
