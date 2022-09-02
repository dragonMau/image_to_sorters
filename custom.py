import tkinter as tk
master = None

    
class Entry(tk.Entry):
    hover = True
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kw_args):
        super().__init__(master, *args, **kw_args)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        
        self.bind("<Enter>", Entry.t_hover)
        self.bind("<Leave>", Entry.f_hover)

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder(True)

    def put_placeholder(self, init=False):
        if not self.get() or self['fg'] == self.placeholder_color or init:
            self.delete(0, "end")
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
            
    def t_hover(e):
        Entry.hover = True
    def f_hover(e):
        Entry.hover = False
    def rbb(e):
        if not Entry.hover:
            master.focus()
    
    def put(self, text: str, placeholder=False) -> None:
        self.delete(0, "end")
        self.insert(0, str(text))
        if placeholder:
            self['fg'] = self.placeholder_color    

class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

    def write(self,string):
        self.text_space.config(state = "normal")
        self.text_space.insert('end', string)
        self.text_space.config(state = "disabled")
        self.text_space.see('end')
    
    def flush(*_):
        pass