#!/usr/bin/python

# For database structure, see
# http://meta.wikimedia.org/wiki/OmegaWiki_data_design#mediaviewer/File:ERD.jpg
# Before running this, need to download and import database
# http://www.omegawiki.org/downloads/omegawiki-lexical.sql.gz (compressed: ~35MB ; uncompressed: ~175MB)

import isocodes, subprocess, itertools, os

languages = ["English", "German", "French", "Spanish", "Italian", "Dutch", "Polish", "Portuguese", "Finnish", "Swedish", "Russian", "Hungarian", "Bulgarian", "Czech", "Hindi"]

combinations = list(itertools.combinations(languages, 2))
print combinations

combination_strings = []
for combination in combinations:
    combination_strings.append("%s-%s" % (combination[0], combination[1]))

print combination_strings

def get_isocode(language_name):
    for lang in isocodes.languages:
        if(lang[1] == language_name):
            return lang[0].upper()

def get_language_name_omegawiki(language_name):
    "Some languages have different names in OmegaWiki"
    return language_name.replace("Spanish", "Castilian")

def run(command):
    print(command)
    code = subprocess.call(command, shell=True)
    if(int(code) != 0):
        exit(1)

sqlcode = """mysql -uroot omega -e "select
convert(GROUP_CONCAT((CASE WHEN language_name = '%O1' THEN spelling END) ORDER BY spelling ASC SEPARATOR ', ') USING utf8) AS %L1,
convert(GROUP_CONCAT((CASE WHEN language_name = '%O2' THEN spelling END) ORDER BY spelling ASC SEPARATOR ', ') USING utf8) AS %L2
from uw_syntrans, uw_expression, language_names
where uw_expression.expression_id = uw_syntrans.expression_id
and language_names.language_id = uw_expression.language_id
and language_names.name_language_id = '85'
group by defined_meaning_id
order by %L1
INTO OUTFILE '%L1-%L2.chemnitz.temp'
FIELDS TERMINATED BY ' :: '
LINES TERMINATED BY '\\n'
;"
"""

javacode = """java -Xmx512m -jar DictionaryBuilder.jar \
--dictOut=%L1-%L2.quickdic \
--lang1=%C1 \
--lang2=%C2 \
--lang1Stoplist=%S1ST.txt \
--lang2Stoplist=%S2ST.txt \
--dictInfo="" \
--input1=%L1-%L2.chemnitz \
--input1Name="" \
--input1Charset=UTF8 \
--input1Format=chemnitz \
--input1FlipColumns=false"""

run("wget -c -q https://github.com/rdoeffinger/DictionaryPC/raw/master/custom_dictionary/DictionaryBuilder.jar")

for language in languages:
    run("wget -c -q http://members.unine.ch/jacques.savoy/clef/%sST.txt" % language.lower())

for combination in combinations:
    print(combination)
    try:
        os.remove('%L1-%L2.chemnitz.temp'.replace("%L1", combination[0]).replace("%L2", combination[1]))
    except:
        pass
    run("# %s - %s" % (combination[0], combination[1]))
    code = sqlcode.replace("%L1", combination[0]).replace("%L2", combination[1])
    code = code.replace("%O1", get_language_name_omegawiki(combination[0])).replace("%O2", get_language_name_omegawiki(combination[1]))
    run(code)
    run("")
    code = """sed -ie 's|\\\\ | |g' %L1-%L2.chemnitz.temp"""
    code = code.replace("%L1", combination[0]).replace("%L2", combination[1])
    run(code)
    run("")
    filename = ""+combination[0]+"-"+combination[1]+".chemnitz"
    f = open(filename + ".temp", "r")
    lines = set(f.readlines()) # sort, uniq
    f.close()
    f = open(filename, "w")
    for line in lines:
        if not "\\N" in line:
            f.write(line)
    f.close()

    code = code.replace("%L1", combination[0]).replace("%L2", combination[1])
    run(code)
    run("")
    code = javacode.replace("%L1", combination[0]).replace("%L2", combination[1])
    code = code.replace("%S1", combination[0].lower()).replace("%S2", combination[1].lower())
    code = code.replace("%C1", get_isocode(combination[0])).replace("%C2", get_isocode(combination[1]))
    run(code)


html = '<table><tr><th></th>'
for language in languages:
    html += '<th>' + language + '</th>'
html += '</tr>'
for rlanguage in languages:
    html += '<tr><td>' + rlanguage + '</td>'
    for clanguage in languages:
        quickdic_file = clanguage + "-" + rlanguage + ".quickdic"
        chemnitz_file = "" + clanguage + "-" + rlanguage + ".chemnitz"
        if "%s-%s" % (clanguage, rlanguage) in combination_strings:
            num_lines = int(sum(1 for line in open(chemnitz_file)))/1000
            cell = "<a href='%s'>%s-%s</a><br>%s" %(quickdic_file, get_isocode(clanguage), get_isocode(rlanguage), num_lines)
        else:
            cell =""
        html += '<td>' + cell + '</td>'
    html += '</tr>'
html += '</table>'
print html
