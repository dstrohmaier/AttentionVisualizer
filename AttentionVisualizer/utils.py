import torch

#--------------------------------------------------------------------------------
# We need to find where each word starts and finishes after tokenization.
# Some words will break down during tokenization (like "going" to "go"+"ing"), and
# we need to loop through the token_ids and say (for example) indexes 10 and 11
# corresponds with the word "going". We do the same thing to find the locations
# of [dot] tokens and stop words as well.
#
# Then we can use these positions to either calculate the score of a multi-part
# word, or ignore the [dot] tokens.
#
# For more information about it, read the blog post mentioned in the README.md
#--------------------------------------------------------------------------------
def find_positions(ignore_specials, ignore_stopwords, the_tokens, stop_words):
    dot_positions = {}
    stopwords_positions = {}
    tmp = []

    if ignore_specials:
        word_counter = 0
        start_pointer = 0
        positions = {}

        num_of_tokens = len( the_tokens )
        num_of_tokens_range = range( num_of_tokens + 1 )

    else:
        word_counter = 1
        start_pointer = 1
        positions = {0: [0, 1]}

        num_of_tokens = len( the_tokens ) - 1
        num_of_tokens_range = range( 1, num_of_tokens + 1 )


    for i in num_of_tokens_range:

        if i == num_of_tokens:
            positions[word_counter] = [start_pointer, i]
            break

        if the_tokens[i][0] in ['Ġ', '.']:

            if ignore_stopwords:
                joined_tmp = "".join(tmp)
                current_word = joined_tmp[1:] if joined_tmp[0] == "Ġ" else joined_tmp
                if current_word in stop_words:
                    stopwords_positions[word_counter] = i-1

            if the_tokens[i] == ".":
                dot_positions[word_counter+1] = i

            positions[word_counter] = [start_pointer, i]
            word_counter += 1
            start_pointer = i
            tmp = []

        tmp.append(the_tokens[i])

    if not ignore_specials:
        positions[len( positions )] = [i, i+1]

    return positions, dot_positions, stopwords_positions

#--------------------------------------------------------------------------------
# Splitting the text into words as a refrence. Then we can map the words to the
# find_positions() function's output.
#--------------------------------------------------------------------------------
def make_the_words(inp, positions, ignore_specials):
    num_of_words = len( positions )

    if ignore_specials:
        the_words = inp.replace(".", " .").split(" ")[0:num_of_words]

    else:
        the_words = inp.replace(".", " .").split(" ")[0:(num_of_words-2)]
        the_words = ['[BOS]'] + the_words + ['[EOS]']

    return the_words

#--------------------------------------------------------------------------------
# A min-max normalizer! We use it to normalize the scores after ignoring some tokens.
#--------------------------------------------------------------------------------
def scale(x, min_, max_):
    return (x - min_) / (max_ - min_)

#--------------------------------------------------------------------------------
# A helper function to use the scores and display each word color-coded.
#--------------------------------------------------------------------------------
def make_html(the_words, positions, final_score, num_words=15):
    the_html = ""

    for i, word in enumerate( the_words ):
        if i in positions:
            start = positions[i][0]
            end   = positions[i][1]

            if end - start > 1:
                score = torch.max( final_score[start:end] )
            else:
                score = final_score[start]

            the_html += """<span style="background-color:rgba(255, 0, 0, {});
                        padding:3px 6px 3px 6px; margin: 0px 2px 0px 2px" title="{}">{}</span>""" \
                        .format(score, score, word)

        if ((i+1) % num_words) == 0:
            the_html += "<br />"

    return the_html

#--------------------------------------------------------------------------------
# Returns a sample article if package is initialized witt "with_sample=True" argument.
#--------------------------------------------------------------------------------
def get_sample_article():
    return """Few persons care to study logic, because everybody conceives himself to be proficient enough in the art of reasoning already. But I observe that this satisfaction is limited to one's own ratiocination, and does not extend to that of other men.

We come to the full possession of our power of drawing inferences, the last of all our faculties; for it is not so much a natural gift as a long and difficult art. The history of its practice would make a grand subject for a book. The medieval schoolman, following the Romans, made logic the earliest of a boy's studies after grammar, as being very easy. So it was as they understood it. Its fundamental principle, according to them, was, that all knowledge rests either on authority or reason; but that whatever is deduced by reason depends ultimately on a premiss derived from authority. Accordingly, as soon as a boy was perfect in the syllogistic procedure, his intellectual kit of tools was held to be complete.

To Roger Bacon, that remarkable mind who in the middle of the thirteenth century was almost a scientific man, the schoolmen's conception of reasoning appeared only an obstacle to truth. He saw that experience alone teaches anything — a proposition which to us seems easy to understand, because a distinct conception of experience has been handed down to us from former generations; which to him likewise seemed perfectly clear, because its difficulties had not yet unfolded themselves. Of all kinds of experience, the best, he thought, was interior illumination, which teaches many things about Nature which the external senses could never discover, such as the transubstantiation of bread. """
