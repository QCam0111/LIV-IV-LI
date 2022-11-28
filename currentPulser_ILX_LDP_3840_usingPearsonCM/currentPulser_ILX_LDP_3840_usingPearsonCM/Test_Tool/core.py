import visa
import ipywidgets
from IPython.display import display

host = r''

rm = visa.ResourceManager()
res_list = rm.list_resources()

Pages = list()
Names = list()

def btn_dec(fun, *args, **kwargs):
    def but_fun(btn):
        btn.disabled = True
        org_desc = btn.description
        btn.description = 'Sweeping'
        try:
            r = fun(btn)
            return r
        except Exception, e:
            print "Sweep failed. Please retry."
            raise e
        finally:
            btn.description = org_desc
            btn.disabled = False

    return but_fun




def show():
    tabs = ipywidgets.Tab(children=Pages)
    for i in tabs.children:
        i.padding = 8
        for j in i.children:
            j.padding = 8
    display(tabs)
    for i in range(len(Names)):
        tabs.set_title(i,Names[i])
