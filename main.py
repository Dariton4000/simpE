from openai import OpenAI
import os
import datetime
import random
import string
import json
from collections import Counter

logs_directory = "logs"
results_directory = "results"

# Todo: Implement multiple models in one run
# leave empty to select currently loaded model (this only works with LM-Studio)
llm = ""
baseurl = "http://127.0.0.1:1234/v1"
reasoning_effort = "medium"

tries = 100

# Todo: When a model responds with more than 120% of what is expected, clasefy the response as critical failature
# Todo: Add option to run with time limit instead of requests limit, e.g. 1 hour instead of 100 tries
# Todo: Implement other benchmarks like adding calculating roots or counting specific characters in a random string/word/sentence, another benchmark to implement would be the model outputing a certain amount of a specific symbol or letter, for example "Output the letter A 27 times with spaces inbetween each letter, but no spaces at the start or end."
# Todo: Save json after each run instead of just at the end


def log_message(message: str) -> None:
    timestamp = starttime.strftime("%Y-%m-%d_%H-%M-%S")
    timestampnow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(logs_directory, f"log_{timestamp}.txt")
    log_filename_recent = os.path.join(logs_directory, f"log_recent.txt")
    # Write to main log file using context manager
    with open(log_filename, "a", encoding="utf-8") as log:
        log.write(f"[{timestampnow}] {message}\n")

    # Write log file which will get deleted and started fresh the next time, so that users can find the most recent log more easily
    with open(log_filename_recent, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")

def write_results(run: dict, model : str) -> None:
    timestamp = starttime.strftime("%Y-%m-%d_%H-%M-%S")
    results_filepath = os.path.join(results_directory, f"result_{model.replace('/', '')}_{timestamp}.json")
    with open(results_filepath, "w") as f:
        json.dump(run, f, indent=2)

def string_reversal(tries, con: console):

    log_message(f"Starting new string reversal eval with {tries} tries")
    
    model = ""

    results = {
        "test_type": "String Reversal",
        "tries": tries,
        "results": []
    }

    client = OpenAI(base_url=baseurl)

    for t in range(tries):
        log_message(f"Starting test {t}")

        result = {
        }


        stringlenth = random.randint(3, 30)
        text = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(stringlenth))

        result["string"] = text

        try:
            starttime = datetime.datetime.now()

            # streaming to support reasoning output
            stream = client.responses.create(
                model=llm,
                reasoning={"effort": reasoning_effort, "summary": "detailed"},
                input=f"Provide the following text in reverse order. Don't output anything else. Only output the reversed string without anything additional, not even quotes: \"{text}\"",
                stream=True,
            )

        except Exception as e:
            print("\nAn error occurred while making the API request.")
            log_message(f"An error occurred in the API call: {e}")
            continue

        reasoning_text = ""
        response = ""
        thinking = False # not used as of now.
        has_thinking = False

        for event in stream:
            if event.type == "response.reasoning_text.delta":
                reasoning_text += event.delta
                thinking = True
                has_thinking = True
                con.thinking(starttime)

            # Todo: Implement reasoning summary collection
            if event.type == "response.reasoning_text.done":
                thinking = False
                has_thinking = True
                log_message(f"[Reasoning]: \n{reasoning_text}")

            elif event.type == "response.output_text.delta":
                response += event.delta
                thinking = False
                
            elif event.type == "response.output_text.done":
                thinking = False

            elif event.type == "response.completed":
                model = event.response.model

        delta = datetime.datetime.now() - starttime

        result["duration_seconds"] = delta.total_seconds()

        if has_thinking:
            result["reasoning"] = reasoning_text


        result["response"] = response

        result["model"] = model

        if response.strip() != text[::-1]:
            log_message(f"Test {t+1} failed. Expected: {text[::-1]}, Got: {response.strip()}")
            result["status"] = "fail"
        else:
            log_message(f"Success: {t+1}")
            result["status"] = "success"

        con.runcomplete((not (response.strip() != text[::-1])), f"String Reversal")

        results["results"].append(result)

    con.benchdone(f"string_reversal")
    return(results)


def add_two_ints(tries, con: console):

    log_message(f"Starting new integer addition eval with {tries} tries")
    
    model = ""

    results = {
        "test_type": "Add two intigers",
        "tries": tries,
        "results": []
    }

    client = OpenAI(base_url=baseurl)

    for t in range(tries):
        log_message(f"Starting test {t}")

        result = {}


        int1_length = random.randint(3, 30)
        int2_length = random.randint(3, 30)

        int1 = int(''.join(random.choice(string.digits) for _ in range(int1_length)))
        int2 = int(''.join(random.choice(string.digits) for _ in range(int2_length)))

        result["int1"] = int1
        result["int2"] = int2

        try:
            starttime = datetime.datetime.now()

            # streaming to support reasoning output
            stream = client.responses.create(
                model=llm,
                reasoning={"effort": reasoning_effort, "summary": "detailed"},
                input=f"Provide the sum of the two numbers. Don't output anything else. Only output the sum of the two numbers without anything additional. Only output the final number, no calculation, no explanation, just the final number without any text.: \"{int1}\" \"{int2}\"",
                stream=True,
            )

        except Exception as e:
            print("\nAn error occurred while making the API request.")
            log_message(f"An error occurred in the API call: {e}")
            continue

        reasoning_text = ""
        response = ""
        thinking = False # not used as of now.
        has_thinking = False

        for event in stream:
            if event.type == "response.reasoning_text.delta":
                reasoning_text += event.delta
                thinking = True
                has_thinking = True
                con.thinking(starttime)

            # Todo: Implement reasoning summary collection
            if event.type == "response.reasoning_text.done":
                thinking = False
                has_thinking = True
                log_message(f"[Reasoning]: \n{reasoning_text}")

            elif event.type == "response.output_text.delta":
                response += event.delta
                thinking = False
                
            elif event.type == "response.output_text.done":
                thinking = False

            elif event.type == "response.completed":
                model = event.response.model


        delta = datetime.datetime.now() - starttime


        result["duration_seconds"] = delta.total_seconds()

        if has_thinking:
            result["reasoning"] = reasoning_text


        result["response"] = response

        result["model"] = model

        try:
            if int(response.strip()) != int1 + int2:
                print(f"\nFail: {t+1}")
                log_message(f"Test {t+1} failed. Expected: {int1 + int2}, Got: {response.strip()}")
                result["status"] = "fail"
            else:
                print()
                print("Success:", t+1)
                log_message(f"Success: {t+1}")
                result["status"] = "success"
        except (ValueError, TypeError):
            print(f"\nFail: {t+1}")
            log_message(f"Test {t+1} failed. Output contained non-numeric characters")
            result["status"] = "fail"

        results["results"].append(result)

    con.benchdone(f"add_two_ints")
    return(results)


def string_rehearsal(tries, con: console):

    log_message(f"Starting new string rehearsal eval with {tries} tries")
    
    model = ""

    results = {
        "test_type": "String Rehearsal",
        "tries": tries,
        "results": []
    }

    client = OpenAI(base_url=baseurl)

    for t in range(tries):
        log_message(f"Starting test {t}")

        result = {
        }


        stringlenth = random.randint(10, 600)
        text = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(stringlenth))

        result["string"] = text

        try:
            starttime = datetime.datetime.now()

            # streaming to support reasoning output
            stream = client.responses.create(
                model=llm,
                reasoning={"effort": reasoning_effort, "summary": "detailed"},
                input=f"Repeat the following string exactly without modifying it. Don't output anything else. Only output the string without anything additional, not even quotes: \"{text}\"",
                stream=True,
            )

        except Exception as e:
            print("\nAn error occurred while making the API request.")
            log_message(f"An error occurred in the API call: {e}")
            continue

        reasoning_text = ""
        response = ""
        thinking = False # not used as of now.
        has_thinking = False

        for event in stream:
            if event.type == "response.reasoning_text.delta":
                reasoning_text += event.delta
                thinking = True
                has_thinking = True
                con.thinking(starttime)

            # Todo: Implement reasoning summary collection
            if event.type == "response.reasoning_text.done":
                thinking = False
                has_thinking = True
                log_message(f"[Reasoning]: \n{reasoning_text}")

            elif event.type == "response.output_text.delta":
                response += event.delta
                thinking = False
                
            elif event.type == "response.output_text.done":
                thinking = False

            elif event.type == "response.completed":
                model = event.response.model


        delta = datetime.datetime.now() - starttime

        result["duration_seconds"] = delta.total_seconds()

        if has_thinking:
            result["reasoning"] = reasoning_text


        result["response"] = response

        result["model"] = model

        if response.strip() != text:
            print(f"\nFail: {t+1}")
            log_message(f"Test {t+1} failed. Expected: {text}, Got: {response.strip()}")
            result["status"] = "fail"
        else:
            print()
            print("Success:", t+1)
            log_message(f"Success: {t+1}")
            result["status"] = "success"

        results["results"].append(result)

    con.benchdone(f"string_rehearsal")
    return(results)

class console():
    def __init__(self, triespb) -> None:
        """
        triespb: tries per benchmark
        """
        self.triespb = triespb
        self.tries_complete = 0
        self.benches_run = 1
        self.currentbench_results = []
        self.current_bench_name = "Happy benchmarking :)"

    def calculatepersentage(self, shouldformat):
        """Calculates the current success rate and returns it as a float or a formated string if bool is set to True"""
        # Todo: needs performance refactor
        counter = 0
        positives = 0
        for result in self.currentbench_results:
            counter += 1
            if result:
                positives +=1

        try:
            per = float(positives/counter)
        except ZeroDivisionError:
            per = 0

        if shouldformat:
            return f"{per:.2%}"
        else:
            return per


    def hub(self, preprint:str):
        print(f"{self.current_bench_name} {self.tries_complete//self.benches_run}/{self.triespb}  {self.calculatepersentage(True)}".ljust(40)) # example: String Reversal 10/100  20% success
        print(preprint.replace("\n", " ").ljust(40), end="\r\033[A")

    def thinking(self, starttime):
        running_for = datetime.datetime.now() - starttime
        # only updates time when token is returned, needs fix for smother stopwatch
        self.hub(f"Thinking... {running_for.total_seconds():.3f}s")

    def runcomplete(self, result:bool, name:str):
        self.currentbench_results.append(result)
        self.tries_complete += 1
        self.current_bench_name = name
        self.hub("Done")


    def benchdone(self, name:str):
        self.benches_run += 1
        print(f"COMPLETE {name}: {self.triespb}/{self.tries_complete/self.benches_run}\nResults: {self.calculatepersentage}", end="\n\n")
        self.currentbench_results.clear() # clears list for next bench



def main():
    global starttime
    starttime = datetime.datetime.now()


    # create logs directory
    try:
        os.mkdir(logs_directory)
        print(f"Directory '{logs_directory}' created successfully.")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{logs_directory}'.")
    except Exception as e:
        print(f"An error occurred, trying to create the logs directory: {e}")

    # creates results directory
    try:
        os.mkdir(results_directory)
        print(f"Directory '{results_directory}' created successfully.")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{results_directory}'.")
    except Exception as e:
        print(f"An error occurred, trying to create the results directory: {e}")

    # removes recent log
    try:
        os.remove(f"{logs_directory}/log_recent.txt")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while removing log_recent.txt: {e}\nIf the file is not present right now, and the rest of the program is working and writing the logs correctly, don't worry.")
    
    con = console(tries)

    lstring_reversal = string_reversal(tries, con)

    ladd_two_ints = add_two_ints(tries, con)

    lstring_rehearsal = string_rehearsal(tries, con)


    run = {
        "string_reversal": lstring_reversal,
        "add_two_ints": ladd_two_ints,
        "string_rehearsal": lstring_rehearsal
    }


    # check if all models are the same, if not, grab the most common model
    all_models = []

    for benchmark in run.values():
        for model in benchmark["results"]:
            all_models.append(model["model"])

    model_counts = Counter(all_models)

    if not all_models:
        log_message("No model could be read, check ^^^above^^^ and your API configuration")
        raise RuntimeError("No model could be read, check the logs and your API configuration")
        

    model = model_counts.most_common(1)[0][0]

    write_results(run, model)
    
    
    



if __name__ == "__main__":
    main()