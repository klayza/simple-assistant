import json
import os
from openai import OpenAI
import toolbox
from dotenv import load_dotenv


load_dotenv()

client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

def ensure_data_directory():
    if not os.path.exists('data'):
        os.makedirs('data')

def init_json_file(file_path, default_content):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
        
def clear_history():
    save_json("data/history.json", [])

def prepare_messages(message):
    ai_data = load_json('data/ai.json')
    history = load_json('data/history.json')
    
    messages = [
        # {"role": "system", "content": "You are a helpful assistant"},
        {"role": "system", "content": ai_data.get('system_prompt', '')},
        {"role": "assistant", "content": ai_data.get('character_prompt', '')},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    return messages

def get_ai_response(messages):
    available_tools = toolbox.get_available_tools()
    tool_instances = {tool.__name__: tool() for tool in available_tools}
    tool_schemas = [instance.schema for instance in tool_instances.values()]

    completion_args = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 1,
        "frequency_penalty": 0.7,
        "presence_penalty": 0,
        "top_p": 1,
    }

    if tool_schemas:
        completion_args["functions"] = tool_schemas
        completion_args["function_call"] = "auto"

    response = client.chat.completions.create(**completion_args)
    print(response)
    # response = ChatCompletion(id='chatcmpl-AAsM3NhuwS88dt8LvItfhYqrhYu9t', choices=[Choice(finish_reason='function_call', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', function_call=FunctionCall(arguments='{"range":20}', name='get_birthdays'), tool_calls=None))], created=1727155583, model='gpt-3.5-turbo-0125', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=15, prompt_tokens=1539, total_tokens=1554, completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0)))
    
    return response.choices[0].message

def handle_function_call(ai_message, messages, tool_instances):
    if ai_message.function_call:
        chosen_tool = tool_instances.get(ai_message.function_call.name)
        print(f"AI used tool: {ai_message.function_call.name} with arguments: " + str(json.loads(ai_message.function_call.arguments)))
        function_to_call = chosen_tool.func
        function_args = json.loads(ai_message.function_call.arguments)
        
        # Call the function with unpacked arguments
        function_response = function_to_call(**function_args)
       
        messages.append(ai_message)
        messages.append({
            "role": "function",
            "name": ai_message.function_call.name,
            "content": str(function_response)
        })
       
        second_response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=1,
            frequency_penalty=0.7,
            presence_penalty=0,
            top_p=1,
        )
        return second_response.choices[0].message
    return ai_message


def update_history(message, reply_text):
    history = load_json('data/history.json')
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply_text})
    save_json('data/history.json', history)

def ai_response(message):
    messages = prepare_messages(message)
    ai_message = get_ai_response(messages)
    
    available_tools = toolbox.get_available_tools()
    
    tool_instances = {tool.__name__: tool() for tool in available_tools}
    ai_message = handle_function_call(ai_message, messages, tool_instances)
    
    reply_text = ai_message.content
    update_history(message, reply_text)
    return reply_text

def init_data_files():
    ensure_data_directory()
    init_json_file('data/ai.json', {
        "system_prompt": "You are a helpful assistant.",
        "character_prompt": "You are ChatGPT, a large language model trained by OpenAI."
    })
    init_json_file('data/history.json', [])

if __name__ == "__main__":
    user_message = "Find birthdays in the next 20 days"
    response = ai_response(user_message)
    print(response)
