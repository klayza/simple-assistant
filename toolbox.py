import openai
import json
from datetime import datetime
from datetime import timedelta
import ai as fractal
from modules.birthdays import check_birthdays
from modules.spotify import find_playlist

registeredTools = []
registeredMicroTools = []


def Tool(cls):
    cls.isTool = True
    registeredTools.append(cls)
    return cls


def MicroTool(cls):
    """
    Tools that only the AI will use, they will give it to their agent to work on, an assistant's assitant
    
    Ex: 
        User: I completed my javascript coding project today!
        AI: *uses tool* <CompleteTask>javascript coding project</CompleteTask>
        def CompleteTask *finds the most similar project to what the user specified*
        AI: I marked it complete! 
    """
    cls.isMicroTool = True
    registeredMicroTools.append(cls)
    return cls


@Tool 
class GetBirthdays:
    def __init__(self):
        self.func = self.get_birthdays
        self.schema = {
            "name": "GetBirthdays",
            "description": "Find people who's birthday is coming up soon given a number of days to look through",
            "parameters": {
                "type": "object",
                "properties": {
                    "range": {
                        "type": "integer",
                        "description": "Range of days too check for birthdays in the future",
                    }
                },
            },
            "required": ["range"],
        }

    def get_birthdays(self, range):
        return check_birthdays(range)
    
    

@Tool 
class FindSpotifyPlaylist:
    def __init__(self):
        self.func = self.get_playlist
        self.schema = {
            "name": "FindSpotifyPlaylist",
            "description": "Find a Spotify playlist based on mood or activity",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords that will best suit the mood or activity",
                    }
                },
            },
            "required": ["query"],
        }
    def get_playlist(self, query):
        find_playlist(query)


# @Tool 
class CompleteTask:
    def __init__(self):
        self.func = self.markTaskComplete
        self.schema = {
            "name": "CompleteTask",
            "description": "Mark a task complete. Only use when a user explicitly says they've completed something",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "The general name of the task",
                    }
                },
            },
            "required": ["task_name"],
        }

    def markTaskComplete(self, userID, generalTaskName):
        tasks = fractal.getUserData(userID).get("tasks")
        tasks = [task for task in tasks if task["status"] != "complete"]

        agent = Agent()
        agent.Load([SelectChoice])
        response = agent.Do(
            prompt=f"Select the choice that is the closest in meaning to '{generalTaskName}'",
            data=self.toEnglish(tasks),
        )
        if response["index"].isdigit:
            return self.setTaskStatus(userID, int(response.get("index")), "complete")
        else:
            return "Task not found"

    def toEnglish(self, tasks):
        taskString = ""
        i = 1
        for task in tasks:
            taskString += str(i) + " - " + task["name"] + "\n"
            i += 1
        return taskString

    def setTaskStatus(self, userID, index, status):
        data = fractal.getUserData(userID)
        data["tasks"][index - 1]["status"] = status
        fractal.setUserData(userID, data)
        return "Task set completed"


# user: hey I did that one task! ai: *detects user completed task* -> markTaskComplete(1349, that one task) -> loadAgent("")


@MicroTool
class SelectChoice:
    def __init__(self):
        self.needID = False
        self.func = self.selectChoice
        self.schema = {
            "name": "SelectChoice",
            "description": "Choose a number to select a choice",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "A number. The number which represents your choice.",
                    }
                },
            },
        }

    # Pseudo-function (Only need for paramaterized responses)
    def selectChoice(self, choice):
        return choice


class Agent:
    def __init__(self):
        self.availableTools = registeredMicroTools
        self.useAvailable = False
        self.loadedTools = []

    def Do(self, prompt, data):
        openai.api_key = fractal.OPENAI_API_KEY
        messages = []
        messages.append(
            {
                "role": "system",
                "content": f"These are your instructions, be organized and highly detailed: {prompt}",
            }
        )
        messages.append({"role": "user", "content": str(data)})
        functions = None
        response = None
        if self.loadedTools:
            toolInstances = {tool.__name__: tool() for tool in self.loadedTools}
            toolSchemas = [instance.schema for instance in toolInstances.values()]
            functions = toolSchemas
        elif self.useAvailable and self.availableTools:
            toolInstances = {tool.__name__: tool() for tool in self.availableTools}
            toolSchemas = [instance.schema for instance in toolInstances.values()]
            functions = toolSchemas
        if functions:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                functions=functions,
                function_call="auto",
            )
            responseMsg = response["choices"][0]["message"]

            if responseMsg.get("function_call"):
                chosenTool = toolInstances.get(responseMsg["function_call"]["name"])
                functionToCall = chosenTool.func

                functionJsonArgs = json.loads(responseMsg["function_call"]["arguments"])

                return functionToCall(functionJsonArgs)

        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613", messages=messages
            )

        return response
        # return response["choices"][0]["message"].get("content")

    def Load(self, toolNames):
        for name in toolNames:
            self.loadedTools.append(name)


def get_available_tools():
    return registeredTools



if __name__ == "__main__":
    # print(CompleteTask().markTaskComplete(
    #     fractal.ADMIN_ID, "Clayton made some type of ramen"))
    # CompleteTask().setTaskStatus(fractal.ADMIN_ID, 4, "complete")
    # pass  # Testing goes here
    # sendSelfie_instance = SendSelfie()
    # sendSelfie_instance.sendSelfie(
    #     fractal.ADMIN_ID,
    #     emotion="happy",
    #     verb="sitting",
    #     place="diner",
    #     condition="night",
    #     nsfw=True,
    # )
    pass
