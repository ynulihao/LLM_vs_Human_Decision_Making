import re
import json


def extract_answers(response: str) -> dict[str, str]:
    """Extracts the answers from the response. The answers are extracted by parsing the json part of the response.
    
    Args:
        response (str): Response from the LLM. The response should have a json code snippet with the answers. For example: ```json{"plan": "go to the kitchen", "goals": "go to the kitchen"}```

    Returns:
        dict[str, str]: Dictionary with the answers.
    """
    patt = re.compile(r'\s*```json\s*([\w\W\n\r\t]*?)\s*```\s*', re.MULTILINE)
    try:
        response = response.replace('\n', ' ') # Remove new lines to avoid errors on multiline double quotes
        answers = re.findall(patt, response)[0].strip() # Get the first json part of the response
        answers = re.sub(r'(:\s*"[^"]+")\s*("[^"]+"\s*:)', r'\1, \2', answers) # Add missing commas between items
        answers = re.sub(r'"\s*,\s*}', '"}', answers) # Remove commas before the closing bracket
        parsed_answers = json.loads(answers)
    except:
        parsed_answers = {}
    return parsed_answers

def extract_text(response: str) -> str:
    """Extracts the answers from the response. The answers are extracted by parsing the ```text ``` part of the response.
    
    Args:
        response (str): Response from the LLM. The response should have a plain text snippet with the answers. For example: ```text\nHello, this is a text answer.\n```

    Returns:
        dict[str, str]: Dictionary with the answers.
    """
    patt = re.compile(r'\s*```text\s*([\w\W\n\r\t]*?)\s*```\s*', re.MULTILINE)
    try:
        response = re.findall(patt, response)[0].strip()
    except:
        response = ''
    return response

def extract_tags(response: str) -> dict:
    """Extract tags from the response. A tag is represented as <tag>content<\tag>, where in this case a dict would be return with the key anything and the value content.
    
    Args:
        response (str): Response from the LLM. The response should have tags like XML tags.

    Returns:
        dict: Dictionary with the tags as keys and the content as values.
    """
    patt = r'<(\w+)>(.*)?</\1>'
    return {k: v.strip() for k, v in re.findall(patt, response, re.DOTALL)}


if __name__ == '__main__':

    # input_str = """
    #                 Response:
    #                 <reasoning>The experiment involves choosing cards from one of four decks to either win or lose money.
    #                 Each deck has different probabilities of winning or losing, with two decks generally being advantageous and
    #                 two being disadvantageous. The current image does not provide information about the decks or the card selection
    #                 interface.</reasoning>
    #                 <choice>2</choice>
    #             """
    #
    # print(extract_tags(input_str))
    #
    # input_str = '''
    #                 Before the answer:
    #                 ```text
    #                 This is the actual text response that needs to be extracted.
    #                 It includes several lines and even some special formatting:
    #                 - List item 1
    #                 - List item 2
    #                 ```
    #                 test
    #                 python
    #             '''
    #
    # print(extract_text(input_str))

    input_str = """
                    Response: 
                    <reasoning>The experiment involves choosing cards from one of four decks to either win or lose money.
                    Each deck has different probabilities of winning or losing, with two decks generally being advantageous and 
                    two being disadvantageous. The current image does not provide information about the decks or the card selection
                    interface.</reasoning> 
                    <choice>2</chice>
                """

    print(extract_tags(input_str))
