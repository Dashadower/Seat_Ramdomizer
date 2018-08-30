import tkinter as tk, tkinter.messagebox, os, pickle, sys, random
from tkinter.constants import *


class RenderCanvas(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, args, kwargs)
        self.master = master
        self.seat_pos = []

    def build_initial_structure(self, number_of_students, group_count, group_columnsize):
        self.delete(ALL)
        self.seat_pad = 5
        self.master.update()
        self.x_buffer = 50
        self.y_buffer = 50
        self.seat_size_x = (self.winfo_width() - self.seat_pad * (group_columnsize - 1) * group_count) / (
        ((group_columnsize) * group_count + (group_count)))
        self.group_pad = self.seat_size_x
        self.seat_size_y = self.seat_size_x / 2
        self.start_position_x = self.x_buffer + self.seat_size_x / 2
        self.start_position_y = self.y_buffer + self.seat_size_y / 2
        self.current_position_x = self.start_position_x
        self.current_position_y = self.start_position_y

        self.seat_pos = []

        while number_of_students >= 0:
            for groupnum in range(group_count):
                for column_num in range(group_columnsize):
                    if number_of_students == 0:
                        return 0
                    self.create_rectangle(self.current_position_x - self.seat_size_x / 2,
                                          self.current_position_y - self.seat_size_y / 2,
                                          self.current_position_x + self.seat_size_x / 2,
                                          self.current_position_y + self.seat_size_y / 2, fill="green")
                    self.seat_pos.append((self.current_position_x, self.current_position_y))
                    self.current_position_x += self.seat_size_x + self.seat_pad
                    number_of_students -= 1
                self.current_position_x += self.group_pad
            self.current_position_x = self.start_position_x
            self.current_position_y += self.seat_size_y + self.seat_pad

            """if self.current_position_x + self.seat_pad + self.seat_size_x > self.winfo_width():
                self.current_position_y += self.seat_pad"""
        self.update()

    def draw_seats(self, number_of_students, group_count, group_columnsize, label_arr=None):
        self.build_initial_structure(number_of_students, group_count, group_columnsize)
        if label_arr:
            label_arr = list(label_arr)
            random.shuffle(label_arr)
            for seat in self.seat_pos:
                self.create_text(seat[0], seat[1], font=("arial", int(self.seat_size_x / 5)), text=label_arr[0])
                label_arr.pop(0)
        else:
            cx = []
            for x in range(1, number_of_students + 1):
                cx.append(x)
            random.shuffle(cx)
            for seat in self.seat_pos:
                self.create_text(seat[0], seat[1], font=("arial", int(self.seat_size_x / 5)), text=str(cx[0]))
                cx.pop(0)


class OptionFrame(tk.Frame):
    def __init__(self, master, renderer_object, *args, **kwargs):
        tk.Frame.__init__(self, args, kwargs)
        self.master = master
        self.renderer_object = renderer_object

        self.toggle_group_options = tk.IntVar()
        self.toggle_group_options.set(1)
        self.student_count = tk.IntVar()
        self.group_count = tk.IntVar()
        self.group_count.set(3)
        self.group_column_size = tk.IntVar()
        self.group_column_size.set(2)

        self.config_frame = tk.Frame(self, bd=2, relief=SUNKEN)
        self.config_frame.grid(row=0, column=0)

        tk.Button(self.config_frame, text="자리 배치하기", command=self.on_generate_seats, bg="yellow", fg="red").pack(
            side=BOTTOM)
        tk.Button(self.config_frame, text="책상 배열하기", command=self.on_create_tables).pack(side=BOTTOM)

        self.group_config_labelframe = tk.LabelFrame(self.config_frame, text="모둠 설정", padx=10, pady=10)
        self.group_config_labelframe.pack(side=BOTTOM, anchor=S)

        tk.Checkbutton(self.config_frame, text="이름목록 사용하기", variable=self.toggle_group_options,
                       command=self.check_group_options).pack(side=BOTTOM, anchor=W)

        tk.Label(self.config_frame, text="학생 수").pack(side=LEFT)
        self.student_count_entry = tk.Entry(self.config_frame, textvariable=self.student_count)
        self.student_count_entry.pack(side=LEFT, anchor=E, fill=X)
        self.student_count_entry.config(state=DISABLED)
        tk.Label(self.group_config_labelframe, text="모둠 수").grid(row=0, column=0)
        tk.Entry(self.group_config_labelframe, textvariable=self.group_count).grid(row=0, column=1)

        tk.Label(self.group_config_labelframe, text="모둠 가로 크기").grid(row=1, column=0)
        tk.Entry(self.group_config_labelframe, textvariable=self.group_column_size).grid(row=1, column=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.student_info_frame = tk.Frame(self, bd=2, relief=SUNKEN)
        self.student_info_frame.grid(row=1, column=0, sticky=(N, E, S, W))

        self.student_listbox = tk.Listbox(self.student_info_frame)
        self.student_listbox.bind("<Double-Button-1>", self.on_student_doubleclick)

        if os.path.exists("students.pickle"):
            student_data_file = open("students.pickle", "rb")
            for student in pickle.load(student_data_file):
                self.student_listbox.insert(END, student)

            student_data_file.close()

        self.student_listbox_yscrollbar = tk.Scrollbar(self.student_info_frame, command=self.student_listbox.yview)
        self.student_listbox.config(yscrollcommand=self.student_listbox_yscrollbar.set)

        self.student_entry_var = tk.StringVar()
        self.student_entry_var.set("학생 이름 입력")
        nameentry = tk.Entry(self.student_info_frame, textvariable=self.student_entry_var)
        nameentry.bind("<Return>", lambda event: self.on_student_add())

        self.student_listbox_yscrollbar.pack(side=RIGHT, fill=Y)
        self.student_listbox.pack(side=BOTTOM, anchor=W, expand=YES, fill=BOTH)

        nameentry.pack(side=LEFT, fill=X, expand=YES, anchor=NW)
        tk.Button(self.student_info_frame, text="입력", command=self.on_student_add).pack(side=LEFT, anchor=NE)
        tk.Button(self.student_info_frame, text="초기화", command=self.on_student_reset).pack(side=LEFT, anchor=NE)

    def on_create_tables(self):
        if self.toggle_group_options.get():
            if len(self.student_listbox.get(0,
                                            END)) == 0 or self.group_count.get() == 0 or self.group_column_size.get() == 0:
                tkinter.messagebox.showinfo("", "학생수, 모둠수, 모둠 크기를 확인해주세요.")
            else:
                self.renderer_object.build_initial_structure(len(self.student_listbox.get(0, END)),
                                                             self.group_count.get(), self.group_column_size.get())
        else:
            if self.student_count.get() == 0:
                tkinter.messagebox.showinfo("", "학생수를 확인해주세요")
            else:
                self.renderer_object.build_initial_structure(self.student_count.get(), self.group_count.get(),
                                                             self.group_column_size.get())

    def on_generate_seats(self):
        if self.toggle_group_options.get():
            if len(self.student_listbox.get(0,
                                            END)) == 0 or self.group_count.get() == 0 or self.group_column_size.get() == 0:
                tkinter.messagebox.showinfo("", "학생수, 모둠수, 모둠 크기를 확인해주세요.")
            else:
                self.renderer_object.draw_seats(len(self.student_listbox.get(0, END)), self.group_count.get(),
                                                self.group_column_size.get(), self.student_listbox.get(0, END))
        else:
            if self.student_count.get() == 0:
                tkinter.messagebox.showinfo("", "학생수를 확인해주세요")
            else:
                self.renderer_object.draw_seats(self.student_count.get(), self.group_count.get(),
                                                self.group_column_size.get())

    def check_group_options(self):
        if self.toggle_group_options.get():
            self.student_count_entry.config(state=DISABLED)
        else:
            self.student_count_entry.config(state=NORMAL)

    def on_student_add(self):
        if not self.student_entry_var.get() or self.student_entry_var.get() == "학생 이름 입력":
            tkinter.messagebox.showinfo("", "학생 이름을 입력해주세요")
        else:
            self.student_listbox.insert(END, self.student_entry_var.get())
            self.student_entry_var.set("")
            with open("students.pickle", "wb") as outfile:
                pickle.dump(self.student_listbox.get(0, END), outfile)
            print(self.student_listbox.get(0, END))

    def on_student_reset(self):
        self.student_listbox.delete(0, END)
        if os.path.exists("students.pickle"):
            os.remove("students.pickle")

    def on_student_doubleclick(self, event):
        if self.student_listbox.curselection():
            self.student_listbox.delete(self.student_listbox.curselection()[0])
            with open("students.pickle", "wb") as outfile:
                pickle.dump(self.student_listbox.get(0, END), outfile)


root = tk.Tk()


def exit_gui():
    root.destroy()
    sys.exit()


root.protocol("WM_DELETE_WINDOW", exit_gui)
root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()))
root.state('zoomed')
root.title("랜덤 자리배치")

rcanvas = RenderCanvas(root, bd=10, relief=RIDGE)
rcanvas.pack(expand=YES, fill=BOTH, side=LEFT)
oframe = OptionFrame(root, rcanvas)
oframe.pack(fill=Y, side=LEFT)
# rcanvas.build_initial_structure(35, 3, 2)


root.mainloop()