import time
import tkinter as tk
from tkinter import filedialog
from ..requesters import *
from PIL import Image, ImageTk
import os
import datetime
import winsound

class PabloApp(object):

    CANVAS_HEIGHT = 400
    CANVAS_WIDTH = 600
    TIME = 240
    
    def __init__(self, master, model):
        super().__init__()
        self._model = model
        self._master = master

        self._image = None
        self._images = []
        self._image_index = 0

        self.initialise_menu()

        self._canvas = tk.Canvas(master, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg='#000')
        self._canvas.pack(side=tk.TOP, expand=True)

        self._prompt = tk.Label(master, text='Prompt: ', font=('Comic Sans', 24))
        self._prompt.pack(side=tk.TOP)

        self._status = StatusBar(master, next=self.next, big_set_paused=self.set_paused, bg='blue')
        self._status.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._default_image = Image.open('uwu.png')
        self.draw_image(None)

        self._paused = True
        self._time = self.TIME
        self.one_second()

    def change_time(self, delta):
        self._time += delta
        self._time = max(0, min(self._time, self.TIME))

    def one_second(self):
        if not self._paused:
            self.change_time(-1)
            if self._time == 0:
                winsound.PlaySound(os.path.join(os.getcwd(), 'sounds', 'stop.wav'), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self._paused = True
                self._status.set_paused(True)

        time_str = datetime.timedelta(seconds=self._time)
        self._status.set_time(time_str)

        self._master.after(1000, self.one_second)

    def initialise_menu(self):
        menubar = tk.Menu(self._master)

        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Select Default Folder", command=self.browse_file_folder)
        filemenu.add_command(label="Open Image", command=self.open_image)
        filemenu.add_separator()
        filemenu.add_command(label="Save Requests", command=self.save)
        filemenu.add_command(label="Load Requests", command=self.load)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # display the menu
        self._master.config(menu=menubar)

    def save(self):
        f = filedialog.asksaveasfilename()
        self._model.get_requester('image').save(f)

    def load(self):
        f = filedialog.askopenfilename()
        self._model.get_requester('image').load(f)

    def populate_images(self, path):
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            image = Image.open(full_path)
            self._images.append(image)

    def browse_file_folder(self):
        filename = filedialog.askdirectory()
        self.populate_images(filename)

    def next(self):
        # first try get prompt from model
        next_image = None
        next_prompt = self._model.get_requester('image').select_random_request()
        
        if next_prompt is None:
            # get from images folder
            if len(self._images) == 0:
                return

            next_image = self._images[self._image_index]
            next_prompt = next_image.filename.split('/')[-1].split('\\')[-1]

            self._image_index = (self._image_index + 1) % len(self._images)

        self.update(next_image, next_prompt)
        self._time = self.TIME

    def draw_image(self, image):
        self._canvas.delete(tk.ALL)
        
        if image is None:
            image = self._default_image

        image = self.resize_image(image)

        self._image = ImageTk.PhotoImage(image)
        self._canvas.create_image((self.CANVAS_WIDTH // 2, self.CANVAS_HEIGHT // 2), image=self._image)

    def update(self, image, prompt):
        self._prompt.config(text=prompt)
        self.draw_image(image)

    def open_image(self):
        path = filedialog.askopenfilename()
        try:
            image = Image.open(path)
        except:
            print('uwu we made a fucky wucky')
        self.draw_image(image)

    def resize_image(self, image):
        width, height = image.size
        c_width, c_height = self.CANVAS_WIDTH, self.CANVAS_HEIGHT

        if width > c_width:
            scale = width / c_width
            image = image.resize((round(width / scale), round(height / scale)))
            width, height = image.size

        if height > c_height:
            scale = height / c_width
            image = image.resize((round(width / scale), round(height / scale)))
        
        return image

    def set_paused(self, paused):
        self._paused = paused

class StatusBar(tk.Frame):
    def __init__(self, master, next, big_set_paused, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        frame = tk.Frame(self, **kwargs)
        self.big_pause = big_set_paused
        self.next = tk.Button(frame, text="next", command=next)
        self.next.pack(side=tk.LEFT, ipadx=20, ipady=10, padx=10, pady=10)

        self.paused = True
        self.play = tk.Button(frame, text="play", command=lambda: self.set_paused(not self.paused))
        self.play.pack(side=tk.LEFT, ipadx=20, ipady=10, padx=10, pady=10)

        self.timer = tk.Label(frame, text="0:00")
        self.timer.pack(side=tk.LEFT, ipadx=20, ipady=10, padx=10, pady=10)

        frame.pack()

    def set_paused(self, paused):
        self.paused = paused
        self.big_pause(self.paused)

        if self.paused:
            self.play.configure(text='Play')
        else:
            self.play.configure(text='Pause')

    def set_time(self, label):
        self.timer.configure(text=label)


def test():
    root = tk.Tk()
    root.title("heyyy")

    #Image.open('uwu.png').show()
    
    m = Model()
    m.set_accepting_requests(True)
    x = PabloApp(root, m)
    m.add_request('RUNNING OUT OF TIME', 'harry')
    root.mainloop()


if __name__ == "__main__":
    test()