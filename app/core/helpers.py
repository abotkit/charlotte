from utilities import logger_config

logger = logger_config.get_logger(__name__)

def parse_intent_examples_to_list(examples: str):
    return [x.replace("- ", "") for x in examples.splitlines()]


def parse_intent_examples_to_string(examples: list):
    tmp = map(lambda x: f"- {x}\n", examples)
    joined_str = "".join(tmp)
    return joined_str


def add_element_to_string(examples: str, example: str):
    joined_str = "".join((examples, '- ', example, '\n'))
    return joined_str


def add_example(data: dict, example: str, intent: str, domain_data: dict):
    index = next((index for (index, d) in enumerate(data['nlu']) if 'intent' in d and d['intent'] == intent), None)
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
        domain_intents = domain_data['intents']
        domain_intents.append(intent)
        domain_data['intents'] = domain_intents
    return data, domain_data


def delete_example(data: dict, example: str, intent: str):
    index = next((index for (index, d) in enumerate(data['nlu']) if 'intent' in d and d['intent'] == intent), None)
    if index is not None:
        examples = parse_intent_examples_to_list(data['nlu'][index]['examples'])
        try:
            examples.remove(example)
        except ValueError as e:
            logger.error(f"Example '{example}' not in data. Ex: {str(e)}")
            return None
        data['nlu'][index]['examples'] = parse_intent_examples_to_string(examples)
        return data


def get_examples(data: dict, intent: str):
    for nlu_intent in data['nlu']:
        if 'intent' in nlu_intent:
            if intent == nlu_intent['intent']:
                return {'name': intent, 'examples': parse_intent_examples_to_list(nlu_intent['examples'])}


def get_all_examples(data: dict):
    parsed_examples = list()
    for intent in data['nlu']:
        if 'intent' in intent:
            parsed_examples.append(dict(
                intent=intent['intent'],
                examples=parse_intent_examples_to_list(intent['examples'])
            ))
    return parsed_examples


def get_intents(data: dict):
    intents = list()
    for intent in data['nlu']:
        if 'intent' in intent:
            intents.append({
                'name': intent['intent'],
                'action': None
            })
    return intents


def get_responses(data: dict):
    # TODO: Add components like buttons, images etc. to return value
    parsed_responses = list()
    for response, elements in data['responses'].items():
        parsed_responses.append(dict(
            response=response,
            examples=[elem['text'] for elem in elements if 'text' in elem]
        ))
    return parsed_responses
