import re

def parse_ennote(self):
    matchObj2 = re.findall(r'<en-note(.*?)>',self, re.M|re.I)
    print "======================"
    for match in matchObj2:
        split = re.split('[ ="]',match)
        count = 0
        for s in split:
            if s != "":
                if count % 2 ==0:
                    print s
                else :
                    print "    :",s
                count+=1
        print "======================"



testsplit = """<en-note title="ggg" hey="abdd" bgcolor="red" text="blue">
hey this is a test <div align="left">ohhhhhh no~~~~~</div><span color="black">good bye gg</span></en-note>
<en-note title="bbbb" lang="abcde">
<div>oh my gosh~~~~~</div>
<span>I am Handsome guy</div></en-note>
"""

parse_ennote(testsplit)
