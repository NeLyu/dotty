import spacy
from transformers import pipeline

class Preprocess:
    def __init__(self, request, nlp, checker):
        self.request = request
        self.doc = nlp(request)
        self.corrections = {'mov': 'move', 
                            'lef': 'left',
                            'jum': 'jump',
                            }
    
    def check_spelling(self, request):
        tokens = [token.text for token in self.doc]
        for word in self.corrections.keys():
            if word in tokens:
                ind = tokens.index(word)
                tokens[ind] = self.corrections[word]
        checked = ' '.join(tokens)
        return checker(checked, max_length=2048)[0]['generated_text']
    
    def has_conjunction(self):
        tokens = [token.text for token in self.doc]
        if 'and' in tokens:
            return True
        
class Command:
    def __init__(self, request, doc, nlp):
        self.request = request
        self.doc = doc
        self.move_seed = "the man goes forward"
        self.jump_seed = "the frog jumps up and hops over"
        self.directions = ['back', 'left', 'right', 'down', 'up', 'back']
        self.colors = ['black', 'color', 'red', 'green', 'blue', 'pink', 'yellow']
        self.verb = ''
        self.where = None
        self.color = None
        self.action = None
    
    def check_attribute(self, doc, attribute_list, attribute_name):
        tokens = [token.text for token in doc]
        for el in attribute_list:
            if el in tokens:
                setattr(self, attribute_name, el)
                return el
        return None
        
    def verb_to_action(self, request, doc):
        verbs = []
        # Print each token and its part-of-speech tag
        print('POS-tagging:')
        for token in doc:
            print("Token and POS", token.text, token.pos_)
            if token.pos_ == 'VERB':
                verbs.append(token.text)
                
        for verb in verbs:
            print('Verb:', verb)
            move = nlp(self.move_seed)
            jump = nlp(self.jump_seed)
            verb_doc = nlp(verb)
            print('Move:', round(move.similarity(verb_doc)))
            print('Jump:', round(jump.similarity(verb_doc)))

            if move.similarity(verb_doc) < jump.similarity(verb_doc):
                self.action = 'jump'
                self.verb = verb
            elif move.similarity(verb_doc) > jump.similarity(verb_doc):
                self.action = 'move'
                self.verb = verb
            elif move.similarity(verb_doc) == jump.similarity(verb_doc):
                self.action = 'move'
                self.verb = verb
            else:
                continue

class Responce:
    def __init__(self, command):
        self.verb = command.verb
        self.color = command.color
        self.where = command.where
        self.adverb = ''
    
    def get_adverb(self):
        if self.color is not None:
            self.adverb += self.color
        elif self.where is not None:
            self.adverb += self.where
        else:
            return ''

    def generate_response(self):
        vowels = ['a', 'e', 'i', 'o', 'u', 'y']
        if self.verb.endswith('e'):
            return self.verb[:-1] + 'ing ' + self.adverb
        elif (len(self.verb) > 2) and (self.verb[-1] not in vowels) and (self.verb[-2] in vowels):
            return self.verb + self.verb[-1] + 'ing ' + self.adverb
        
        else:
            return self.verb + 'ing ' + self.adverb

        
def get_action(text, command, doc):
    command.verb_to_action(text, doc)
    command.check_attribute(doc, command.directions, "where")
    command.check_attribute(doc, command.colors, "color")
    
    if command.color is not None:
        return command.color
    elif command.where is not None and command.action is not None:
        return '_'.join([command.action, command.where])
    elif command.where is not None and command.action is None:
        return command.where
    elif command.where is None and command.action is not None:
        return command.action    
    else:
        return 'idk'
        
    
nlp = spacy.load("en_core_web_lg")
checker = pipeline("text2text-generation","oliverguhr/spelling-correction-english-base")

def process_input(input_text):
    print(input_text)
    input_text = input_text.lower()
    preproc = Preprocess(input_text, nlp, checker)
    #1) Check spelling 
    text = preproc.check_spelling(input_text)
    text = text.lower()
    doc = nlp(text)

    #2) Get action
    command = Command(text, doc, nlp)
    action = get_action(text, command, doc)
    print('Action:', action)

    #3) Generate response
    response = Responce(command)
    response.get_adverb()
    reaction = response.generate_response()
    print('Response:', reaction)
    
    return action, reaction
        
if __name__ == '__main__':
    input_text = input()
    process_input(input_text)
