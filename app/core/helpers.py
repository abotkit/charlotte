def parse_intent_examples_to_list(examples: str):
    return [x.replace("- ", "") for x in examples.splitlines()]


def parse_intent_examples_to_string(examples: list):
    tmp = map(lambda x: f"- {x}\n", examples)
    joined_str = "".join(tmp)
    return joined_str


def add_element_to_string(examples: str, example: str):
    joined_str = "".join((examples, '- ', example, '\n'))
    return joined_str


def add_example(data: dict, example: str, intent: str):
    index = next((index for (index, d) in enumerate(data['nlu']) if d['intent'] == intent), None)
    if index is not None:
        examples = add_element_to_string(data['nlu'][index]['examples'], example)
        data['nlu'][index]['examples'] = examples
    else:
        intents = data['nlu']
        intents.append({
            'intent': intent,
            'examples': f"- {example}\n"
        })
        data['nlu'] = intents
    return data


def delete_example(data: dict, example: str, intent: str):
    index = next((index for (index, d) in enumerate(data['nlu']) if d['intent'] == intent), None)
    if index is not None:
        examples = parse_intent_examples_to_list(data['nlu'][index]['examples'])
        examples.remove(example)
        data['nlu'][index]['examples'] = parse_intent_examples_to_string(examples)
        return data


def get_examples(data: dict, intent: str):
    for nlu_intent in data['nlu']:
        if intent == nlu_intent['intent']:
            return {'name': intent, 'examples': parse_intent_examples_to_list(nlu_intent['examples'])}


def get_all_examples(data: dict):
    parsed_examples = list()
    for intent in data['nlu']:
        parsed_examples.append(dict(
            intent=intent['intent'],
            examples=parse_intent_examples_to_list(intent['examples'])
        ))
    return parsed_examples


def get_intents(data: dict):
    return [{'name': intent, 'action': None} for intent in data['intents']]


def get_responses(data: dict):
    # TODO: Add components like buttons, images etc. to return value
    parsed_responses = list()
    for response, elements in data['responses'].items():
        parsed_responses.append(dict(
            response=response,
            examples=[elem['text'] for elem in elements if 'text' in elem]
        ))
    return parsed_responses
