import re

# parse tag en-note by ' ="
# return list of all en-note attribute
def parse_ennote(self):
    matchObj2 = re.findall(r'<en-note(.*?)>',self, re.M|re.I)
    result_list = []
    for match in matchObj2:
        split = re.split('[\' ="]',match)
        temp_list = []
        for s in split:
            if s != "":
                temp_list.append(s)
        result_list.append(temp_list)
    return result_list

