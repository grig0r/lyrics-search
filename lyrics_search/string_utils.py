import re

def remove_non_letters(word):
    non_text = re.compile(r'[^\w\s]')
    word = non_text.sub(' ', word)
    return word

def string_contained(text, context):
    text, context = map(remove_non_letters, (text, context))
    count = 0
    searched_words = re.split(r'\s', text)
    for word in searched_words:
        searched = re.compile(r'(^|\s){}($|\s)'.format(word), re.I)
        if searched.search(context):
            count += 1
            context = searched.sub(r' ', context, count=1)
    return count, len(searched_words)

def string_contained_percentage(text, context):
    found, length = string_contained(text, context)
    return found / length

def string_overlap_percentage(text1, text2):
    found1, full1 = string_contained(text1, text2)
    found2, full2 = string_contained(text2, text1)
    percentage = (found1 + found2) / (full1 + full2)
    return percentage
