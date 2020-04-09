from utilities import *
from tkinter import *
from tkinter import filedialog


class Client:
    def main_window(self):
        tk = Tk()
        tk.geometry('600x450')
        tk.title('PDF Translator')
        # 主背景
        f = Frame(tk, bg='#3C3F41', width=600, height=450)
        f.place(x=0, y=0)
        # 欢迎
        text = StringVar()
        text.set("欢迎使用PDF翻译器，请选择PDF文件")
        Label(f, fg="#00FA92", bg='#3C3F41', font="Courier, 20", textvariable=text).place(x=120, y=10, anchor=NW)

        bt_file = Button(f, bg='#3C3F41', fg='#000000', text="选择文件", font="Arial, 18",
                         command=lambda: self.file())
        bt_file.place(x=300, y=200, anchor=CENTER)
        tk.mainloop()

    def file(self):
        root = Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(title='请选择发送的文件')
        if filename:
            name = filename.split('.')[-1]
            if name != 'pdf':
                self.error_msg('请选择PDF文件')
            else:
                pdf2_image(filename)
                trans_pic()
                image2_pdf()
                self.error_msg('翻译完成！')
        else:
            self.error_msg('选择文件出错')

    def error_msg(self, info):
        """错误提示界面"""
        errtk = Tk()
        errtk.geometry('250x120')
        errtk.title("提示")
        frame = Frame(errtk, bg='#3C3F41')
        frame.pack(expand=YES, fill=BOTH)
        Label(frame, bg='#3C3F41', fg='#00FA92', text=info).pack(padx=5, pady=20, fill='x')
        bt = Button(frame, text="确定", bg='#3C3F41', fg='#000000', command=errtk.destroy).pack()
        errtk.mainloop()

    def __main__(self):
        self.main_window()


if __name__ == '__main__':
    client = Client()
    client.__main__()
