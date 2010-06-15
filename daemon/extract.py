import re

f = open('text.html')

p = re.compile(r'<.*?>')

body = False
script_style = False
for line in f:
    markupf = 0.0
    textf = len(line)
    line = line.lstrip().rstrip()
    if (line.find('<body')!=-1):
        body = True
    if (line.find('</body')!=-1):
        body = False
    if body==False:
        continue
    if (line.find('<script')!=-1) or (line.find('<style')!=-1):
        script_style = True
    if (line.find('</script')!=-1) or (line.find('</style')!=-1):
        script_style = False
    if script_style==True:
        continue
    index = 0
    sublines = line.split('<br')
    for subline in sublines:
        markup_now = False
        quote_now = False
        for char in subline:
            if (char == '<'):
                markup_now = True
            if (char == '"' and quote_now==False):
                quote_now = True
            else:
                if (char == '"' and quote_now==True):
                    quote_now = False           
            if markup_now or quote_now:
                markupf += 1
            if char == '>':
                markup_now = False
        factor = markupf/textf
        if (factor<0.4):
            subline = p.sub('', subline)
            if len(subline)>32:
                print subline
