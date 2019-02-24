# Perutbation operations
import numpy as np
np.random.seed(seed=300)
import spacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load(
    'en_core_web_sm', parser=False, entity=False, matcher=False, add_vectors=False, tagger=True
)

class Perturb(object):
    def __init__(self, opt):
        self.opt = opt
        self.splitter = "\n"
        print("Perturber created !")

    def perturb(self, act):
        if self.opt['perturb'] == 'None':
            return act
        turns = self._get_turns(act)
        if len(turns) < 3:
            print("less than 3 turns")
            print("turns : {}".format(act['text']))
            return act
        if 'random' in self.opt['perturb']:
            perturb_op = np.random.choice(
                [self.swap, self.drop, self.repeat, self.word_drop]
            )
            turns = perturb_op(turns)
        elif "shuffle" in self.opt['perturb']:
            turns = self.shuffle(turns)
        elif "reverse_utr_order" in self.opt['perturb']:
            turns = self.reverse_utr_order(turns)
        elif "only_last" in self.opt['perturb']:
            turns = self.only_last(turns)
        elif "worddrop" in self.opt['perturb']:
            turns = self.word_drop(turns)
        elif "verbdrop" in self.opt['perturb']:
            turns = self.verb_drop(turns)
        elif "noundrop" in self.opt['perturb']:
            turns = self.noun_drop(turns)
        elif "drop" in self.opt['perturb']:
            turns = self.drop(turns)
        elif "swap" in self.opt['perturb']:
            turns = self.swap(turns)
        elif "repeat" in self.opt['perturb']:
            turns = self.repeat(turns)
        else:
            assert "Invalid perturb mode : {}. Valid : random, drop, swap, repeat".format(self.opt['perturb'])

        self._update_act(turns, act)
        return act

    def swap(self, turns):
        if "first" in self.opt['perturb']:
            pos = [0, 1]
        elif "last" in self.opt['perturb']:
            last_id = len(turns) - 1
            pos = [last_id - 1, last_id]
        else:
            pos = np.random.randint(len(turns), size=2)
        tmp = turns[pos[0]]
        turns[pos[0]] = turns[pos[1]]
        turns[pos[1]] = tmp
        return turns

    def drop(self, turns, pos=None):
        if "first" in self.opt['perturb']:
            pos = 0
        elif "last" in self.opt['perturb']:
            pos = len(turns) - 1
        else:
            pos = np.random.randint(len(turns))
        return [turn for idx, turn in enumerate(turns) if idx != pos]

    def repeat(self, turns, pos=None):
        if "first" in self.opt['perturb']:
            pos = 0
        elif "last" in self.opt['perturb']:
            pos = len(turns) - 1
        else:
            pos = np.random.randint(len(turns))
        return turns[:pos] + [turns[pos]] + turns[pos:]

    def word_drop(self, turns, pos=None):
        if "first" in self.opt['perturb']:
            pos = 0
        elif "last" in self.opt['perturb']:
            pos = len(turns) - 1
        else:
            pos = 'all'

        if pos == 'all':
            modified_turns = []
            for turn in turns:
                word_mask = np.random.binomial(
                    size=len(turn.split()), n=1, p=0.3
                )
                modified_turn = ' '.join(
                    [x for idx, x in enumerate(turn.split()) if word_mask[idx] == 0]
                )
                modified_turns.append(modified_turn)
            return modified_turns
        else:
            # Tune word dropout prob?
            word_mask = np.random.binomial(
                size=len(turns[pos].split()), n=1, p=0.3
            )
            modified_turn = ' '.join(
                [x for idx, x in enumerate(turns[pos].split()) if word_mask[idx] == 0]
            )
            return turns[:pos] + [modified_turn] + turns[pos:]

    def only_last(self, turns):
        return [turns[-1]]

    def reverse_utr_order(self, turns):
        return turns[::-1]

    def shuffle(self, turns):
        np.random.shuffle(turns)
        return turns

    def verb_drop(self, turns):
        if "first" in self.opt['perturb']:
            pos = 0
        elif "last" in self.opt['perturb']:
            pos = len(turns) - 1
        else:
            pos = 'all'

        if pos == 'all':
            modified_turns = []
            for turn in turns:
                processed_turn = nlp(turn)
                modified_turn = ' '.join([x.text for x in processed_turn if x.pos_ != 'VERB'])
                modified_turns.append(modified_turn)
            return modified_turns
        else:
            turn = turns[pos]
            processed_turn = nlp(turn)
            modified_turn = ' '.join([x.text for x in processed_turn if x.pos_ != 'VERB'])
            return turns[:pos] + [modified_turn] + turns[pos:]

    def noun_drop(self, turns):
        if "first" in self.opt['perturb']:
            pos = 0
        elif "last" in self.opt['perturb']:
            pos = len(turns) - 1
        else:
            pos = 'all'

        if pos == 'all':
            modified_turns = []
            for turn in turns:
                processed_turn = nlp(turn)
                modified_turn = ' '.join([x.text for x in processed_turn if x.pos_ != 'NOUN'])
                modified_turns.append(modified_turn)
            return modified_turns
        else:
            turn = turns[pos]
            processed_turn = nlp(turn)
            modified_turn = ' '.join([x.text for x in processed_turn if x.pos_ != 'NOUN'])
            return turns[:pos] + [modified_turn] + turns[pos:]

    def _get_turns(self, act):
        return act['text'].split('\n')

    def _update_act(self, turns, act):
        act['text'] = self.splitter.join(turns)
