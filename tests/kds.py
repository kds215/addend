

import re

# multi line comment check for single line "\"" start & end
MLC1Ldq_regex = re.compile(r'^.*((\"{3}).+(\"{3})){1}.*$') #ok

# multi line comment check for single line '\'' start & end
MLC1Lsq_regex = re.compile(r'^.*((\'{3}).+(\'{3})){1}.*$')  #ok


# multi line comment check for start or end in line for "\""
MLCdq_regex = re.compile(r'.*(\"{3}\s*){1,1}.*')

# multi line comment check for start or end in line for '\''
MLCsq_regex = re.compile(r'.*(\'{3}\s*){1,1}.*') 

text_1dq = '     dvcsvnb  """ sfvgmpse    kdfvnfnv '
text_1sq = "     dvcsvnb  ''' sfvgmpse    kdfvnfnv "

text_2dq = '     dvcsvnb  """ sfvgmpse   """ kdfvnfnv '
text_2sq = "     dvcsvnb  ''' sfvgmpse   ''' kdfvnfnv " #ok

def test_it( name, reg, text):
    print(name)
    match = reg.search(text)

    if match:
        print(f"reg: {reg} ; text: {text}")
        len_groups = len(match.groups())
        print(f"len_group: {len_groups}")

        if len_groups > 0:
            print(f"g(1): " + match.group(1))
        if len_groups > 1:
            print(f"g(2): " + match.group(2))

for text in [text_1dq,text_1sq,text_2dq,text_2sq]:
    test_it("MLC1Ldq_regex",MLC1Ldq_regex,text)
    test_it("MLC1Lsq_regex",MLC1Lsq_regex,text)
    test_it("MLCdq_regex",MLCdq_regex,text)
    test_it("MLCsq_regex",MLCsq_regex,text)