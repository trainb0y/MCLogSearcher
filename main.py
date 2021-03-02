#! python3
import re, gzip, datetime, os, platform, getpass, time
import tkinter as tk
from tkinter.ttk import Progressbar


class MainWindow(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master = master
        self.master.logs = {}
        self.master.title("Log Searcher")
        self.create_widgets()
        self.grid() # does this even get run?

    def create_widgets(self):
        ### Loading data
        self.load_range_label = tk.Label(self,text="Date Range to Load:")
        self.load_range_label.grid(row=0,column=0)

        self.load_range_menu = None
        self.date_range_StringVar = tk.StringVar()
        self.date_range_StringVar.set("Last day")
        self.sortByMenu = tk.OptionMenu(self, self.date_range_StringVar, "Last day","Last week","Last 2 weeks","Last month","All time")
        self.sortByMenu.grid(row=0,column=2)

        self.load_range_button = tk.Button(self,text="Load",command=self.load_files)
        self.load_range_button.grid(row=0,column=4)
        ### End Loading Data
        self.search_label = tk.Label(self,text="Search Text: ")
        self.search_label.grid(row=1,column=0)
        self.search_StringVar = tk.StringVar()
        self.search_StringVar.set("")
        self.search_entry = tk.Entry(self,textvariable=self.search_StringVar,width=30)
        self.search_entry.grid(row=1,column=1,columnspan=3)
        self.search_button = tk.Button(self,text="Search",command=self.search)
        self.search_button.grid(row=1,column=4)


        self.temp = tk.Button(self,text="Temp",command=self.temp).grid(row=3,column=0)

    def temp(self): print(self.master.logs)
    def search(self):
        # Needs to search all of the loaded text, and output a preview
        pass

    def load_files(self):
        # Load all of the files in the specified date range
        LoadWindow(self.master,self.date_range_StringVar.get())

class LoadWindow(tk.Toplevel):
    def __init__(self,master,date_range):
        super().__init__(master = master) 
        self.title("Loading Files") 
        self.date_range = date_range
        self.create_widgets()
        self.grid()
    
    def create_widgets(self):
        self.progress_StringVar = tk.StringVar()
        self.progress_StringVar.set("Loading Files: 0/0")
        self.progress_label = tk.Label(self,textvariable=self.progress_StringVar)
        self.progress_label.grid(row=0,column=0)
        self.progress_bar = Progressbar(self, orient = tk.HORIZONTAL, 
            length = 100, mode = 'determinate') 
        self.progress_bar.grid(row=1,column=0)

        self.progress_bar['value'] = 0
        self.load()
    
    def load(self):
        # Ok, so now we need to figure out what files to load
        # Minecraft has logs formatted YYYY-MM-DD-num.log.gz

        # today = time.strftime("%Y-%m-%d",time.localtime())
        # print(today)

        offsets = {"Last day":1,"Last week":7,"Last 2 weeks":14,"Last month":30,"All time":99999} # I mean technically its not all time but eh
        offset = offsets[self.date_range]

        today = datetime.datetime.now()
        oldest_date = today - datetime.timedelta(days=offset)
      
        # Ok we have the oldest date, time to find the matching files
        user = getpass.getuser()
        if platform.system() == "Windows":
            log_path = f"C:/Users/{user}/AppData/Roaming/.minecraft/logs"
        else: log_path = f"/Users/{user}/Library/Application Support/minecraft/logs"
        

        chat_regex = re.compile(r"(\[\d+:\d+:\d+\] \[main/INFO\]: \[CHAT\])( .*)")
        found_files = []
        for file in os.listdir(log_path):
            try:
                day_str = file.split(".")[0]
                day_str = day_str.split("-")
                day_str = f"{day_str[0]}-{day_str[1]}-{day_str[2]}"
            except: day_str = "0001-01-01" # might be a non-standard log.

            
            day_datetime = datetime.datetime.strptime(day_str, "%Y-%m-%d")
            if day_datetime > oldest_date:
                # We want this file!
                found_files.append(os.path.join(log_path, file))
        
        for file in found_files:
            self.update() # this forces a refresh of the screen
                        # it DOES slow down the program, but for people with years
                        # of logs I think its better that it takes a while and provides feedback
                        # instead of just seeming to hang.

                        # Without this the bar just appears full, and nothing loads until its done
                        # extracting chat.

            self.progress_StringVar.set(f"Loading Files: {found_files.index(file)+1}/{len(found_files)}")
            self.progress_bar['value'] = self.progress_bar['value'] + 100/len(found_files)


            output = []
            if file.endswith(".gz"):
                f = gzip.open(file,"rt")
            else: f = open(file,"r")
            for chat_line in chat_regex.findall(f.read()): # For all lines of chat
                output.append(chat_line[1])   # Add the line to the lines of chat

            f.close() 
            self.master.logs[day_str] = "\n".join(output)

        self.destroy_button = tk.Button(self,text="OK",command=self.destroy)
        self.destroy_button.grid(row=3)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry()
    app = MainWindow(root)
    app.mainloop()

