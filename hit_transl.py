import re


def create_fst_lang():
    fst = {('hit', '<font'): 'sum', ('hit', '<i>'): 'hit', ('sum', '</font>'): 'hit', ('sum', '<font'): 'sum',
           ('sum', '<i>'): 'akk', ('akk', '</font>'): 'hit', ('akk', '<font'): 'sum', ('akk', '<i>'): 'hit'}
    return fst


def create_fst_letters():
    fst = {('aa', 'beg'): 'ā', ('ee', 'beg'): 'ē', ('ii', 'beg'): 'ī', ('uu', 'beg'): 'ū', ('aa', 'end'): 'ā',
           ('ee', 'end'): 'ē', ('ii', 'beg'): 'ī', ('uu', 'end'): 'ū', ('aa', ''): 'a', ('ee', ''): 'e',
           ('ii', ''): 'i', ('uu', ''): 'u', ('āa', ''): 'ā', ('ēe', ''): 'ē', ('īi', ''): 'ī', ('ūu', ''): 'ū',
           ('aa', 'mid'): 'ā', ('ee', 'mid'): 'ē', ('ii', 'mid'): 'ī',('uu', 'mid'): 'ū', ('aaa', ''): 'ā',
           ('eee', ''): 'ē', ('iii', ''): 'ī', ('uuu', ''): 'ū', ('s', ''): 'š', ('h', ''): 'ḫ'}
    return fst


def valid_tag(tag):
    if tag in ['<i>', '</font>']:
        return tag
    if tag.startswith('<font'):
        return '<font'
    return ''


def process_single_v(word):
    single_vowels = {}
    dashes = 0
    for i in range(len(word)):
        if word[i] == '-':
            dashes += 1
        if word[i] in ['a', 'á', 'e', 'é', 'i', 'í', 'u', 'ú']:
            if i == 0:
                single_vowels[0] = 'beg'
            elif (i == len(word) - 1) & (word[i-1] == '-'):
                single_vowels[len(word) - 1 - dashes] = 'end'
            elif i != len(word) - 1:
                if word[i-1] == word[i+1] == '-':
                    single_vowels[i - dashes] = 'mid'
    return single_vowels


def process_word(word):
    new_word = ''
    vowels = ['a', 'á', 'e', 'é', 'i', 'í', 'u', 'ú']
    single_vowels = process_single_v(word)
    fst_letters = create_fst_letters()
    word = clean(word)
    l = len(word)
    for k in range(l):
        if (word[k], '') in fst_letters:
            new_word += fst_letters[(word[k], '')]
            continue
        if k in single_vowels:
            if k != 0:
                if (new_word[k-1]+word[k], single_vowels[k]) in fst_letters:
                    new_letter = fst_letters[(new_word[k-1]+word[k], single_vowels[k])]
                    new_word = new_word[:-1] + '$' + new_letter
                    continue
            if k != len(word)-1:
                if (word[k]+word[k+1], single_vowels[k]) in fst_letters:
                    new_word += fst_letters[(word[k]+word[k+1], single_vowels[k])]
                    word = word[:k + 1] + '$' + word[k + 2:]
                    continue
        if (k != len(word) - 1) & (k != 0):
            if (new_word[k - 1] in vowels) & (word[k + 1] in vowels) & (word[k] == 'i'):
                new_word += 'y'
                continue
            if (new_word[k - 1] + word[k] + word[k + 1], '') in fst_letters:
                new_word = new_word[:-1] + '$'
                word = word[:k + 1] + '$' + word[k + 2:]
                new_word += fst_letters[(new_word[k - 1] + word[k] + word[k + 1], '')]
                continue
        if k != 0:
            if (new_word[k-1]+word[k], '') in fst_letters:
                new_letter = fst_letters[(new_word[k-1]+word[k], '')]
                new_word = new_word[:-1] + '$' + new_letter
                continue
        new_word += word[k]
    return new_word.replace('$', '')


def clean(word):
    word = re.sub('[^-a-záéíúšḫ\s]', '', word)
    clean_word = ''
    for i in range(len(word)):
        if (i != len(word)-1) & (i != 0):
            if word[i] != '-':
                clean_word += word[i]
        else:
            clean_word += word[i]
    return clean_word


def convert_text(file):
    f = open(file, 'r', encoding='utf-8')
    all = f.read()
    long = re.split(r'<body lang="en-GB" dir="ltr">', all)[1]
    tag_text = ''
    word = ''
    text = re.split(r'<body lang="en-GB" dir="ltr">', all)[0] + '<body lang="en-GB" dir="ltr">'
    lang = 'hit'
    sup = False
    fst_lang = create_fst_lang()
    tag = False
    for l in range(len(long)):
        if long[l] == '<':
            word = process_word(word.lower())
            if not sup:
                text += lang_case(word, lang)
            else:
                if '</sup>' in tag_text:
                    if not lang == 'hit':
                        text += tag_text + lang_case(word, lang)
                    sup = False
                else:
                    tag_text += lang_case(word, lang)
            word = ''
            if not sup:
                tag_text = '<'
            else:
                tag_text += '<'
            tag = True
        elif long[l] == '>':
            tag_text += long[l]
            tag = False
            if valid_tag(tag_text) != '':
                lang = fst_lang[(lang, valid_tag(tag_text))]
            if tag_text == '<sup>':
                sup = True
            if not sup:
                text += tag_text
        else:
            if tag:
                tag_text += long[l]
            else:
                if long[l].isupper():
                    lang = fst_lang[(lang, '<font')]
                word += long[l]
    write_new_text(text)


def lang_case(word, lang):
    if lang != 'hit':
        return word.upper()
    else:
        return word

def write_new_text(text):
    f = open('new_text.html', 'w', encoding='utf-8')
    f.write(text)
    f.close()


if __name__ == '__main__':
    convert_text('syllab.html')
